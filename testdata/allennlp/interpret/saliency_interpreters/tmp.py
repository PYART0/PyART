import math
from typing import List, Dict, Any

import numpy

from allennlp.common.util import JsonDict, sanitize
from allennlp.data import Instance
from allennlp.interpret.saliency_interpreters.saliency_interpreter import SaliencyInterpreter
from allennlp.nn import util


@SaliencyInterpreter.register("integrated-gradient")
class IntegratedGradient(SaliencyInterpreter):

    def saliency_interpret_from_json(self, inputs: JsonDict) -> JsonDict:
        labeled_instances = self.predictor.json_to_labeled_instances(inputs)

        instances_with_grads = dict()
        for idx, instance in enumerate(labeled_instances):
            grads = self._integrate_gradients(instance)

            for key, grad in grads.items():
                embedding_grad = numpy.sum(grad[0], axis=1)
                norm = numpy.linalg.norm(embedding_grad, ord=1)
                normalized_grad = [math.fabs(e) / norm for e in embedding_grad]
                grads[key] = normalized_grad

            instances_with_grads["instance_" + str(idx + 1)] = grads

        return sanitize(instances_with_grads)

    def _register_forward_hook(self, alpha: int, embeddings_list: List):

        def forward_hook(module, inputs, output):
            if alpha == 0:
                embeddings_list.append(output.squeeze(0).clone().detach().numpy())

            output.mul_(alpha)

        embedding_layer = util.find_embedding_layer(self.predictor._model)
        handle = embedding_layer.register_forward_hook(forward_hook)
        return handle

    def _integrate_gradients(self, instance: Instance) -> Dict[str, numpy.ndarray]:
        ig_grads: Dict[str, Any] = {}

        embeddings_list: List[numpy.ndarray] = []

        steps = 10

        for alpha in numpy.linspace(0, 1.0, num=steps, endpoint=False):
            handle = self._register_forward_hook(alpha, embeddings_list)

            grads = self.predictor.get_gradients([instance])[0]
            handle.remove()

            if ig_grads == {}:
                ig_grads = grads
            else:
                for key in grads.keys():
                    ig_grads[key] += grads[key]

        for key in ig_grads.keys():
            ig_grads[key] /= steps
        reveal_type(embeddings_list)