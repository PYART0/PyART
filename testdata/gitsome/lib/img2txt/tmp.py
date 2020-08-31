import sys
from docopt import docopt


def HTMLColorToRGB(colorstring):
    colorstring = colorstring.strip()
    if colorstring[0] == '#':
        colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError(
            "input #{0} is not in #RRGGBB format".format(colorstring))
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)


def alpha_blend(src, dst):
    src_multiplier = (src[3] / 255.0)
    dst_multiplier = (dst[3] / 255.0) * (1 - src_multiplier)
    result_alpha = src_multiplier + dst_multiplier
    if result_alpha == 0:       # special case to prevent div by zero below
        return (0, 0, 0, 0)
    else:
        return (
            int(((src[0] * src_multiplier) +
                (dst[0] * dst_multiplier)) / result_alpha),
            int(((src[1] * src_multiplier) +
                (dst[1] * dst_multiplier)) / result_alpha),
            int(((src[2] * src_multiplier) +
                (dst[2] * dst_multiplier)) / result_alpha),
            int(result_alpha * 255)
        )


def getANSIcolor_for_rgb(rgb):
    websafe_r = int(round((rgb[0] / 255.0) * 5))
    websafe_g = int(round((rgb[1] / 255.0) * 5))
    websafe_b = int(round((rgb[2] / 255.0) * 5))
    return int(((websafe_r * 36) + (websafe_g * 6) + websafe_b) + 16)


def getANSIfgarray_for_ANSIcolor(ANSIcolor):
    return ['38', '5', str(ANSIcolor)]


def getANSIbgarray_for_ANSIcolor(ANSIcolor):
    return ['48', '5', str(ANSIcolor)]


def getANSIbgstring_for_ANSIcolor(ANSIcolor):
    return "\x1b[" + ";".join(getANSIbgarray_for_ANSIcolor(ANSIcolor)) + "m"


def generate_ANSI_to_set_fg_bg_colors(cur_fg_color, cur_bg_color, new_fg_color,
                                      new_bg_color):


    color_array = []

    if new_bg_color != cur_bg_color:
        if new_bg_color is None:
            color_array.append('49')        # reset to default
        else:
            color_array += getANSIbgarray_for_ANSIcolor(new_bg_color)
    if new_fg_color != cur_fg_color:
        if new_fg_color is None:
            color_array.append('39')        # reset to default
        else:
            color_array += getANSIfgarray_for_ANSIcolor(new_fg_color)
    if len(color_array) > 0:
        return "\x1b[" + ";".join(color_array) + "m"
    else:
        return ""


def generate_ANSI_from_pixels(pixels, width, height, bgcolor_rgba,
                              get_pixel_func=None, is_overdraw=False):
    if get_pixel_func is None:
        get_pixel_func = lambda pixels, x, y: (" ", pixels[x, y])
    if bgcolor_rgba is not None:
        bgcolor_ANSI = getANSIcolor_for_rgb(bgcolor_rgba)
        bgcolor_ANSI_string = getANSIbgstring_for_ANSIcolor(bgcolor_ANSI)
    else:
        bgcolor_ANSI = None
        bgcolor_ANSI_string = "\x1b[49m"
    string = "\x1b[0m"
    prior_fg_color = None       # this is an ANSI color not rgba
    prior_bg_color = None       # this is an ANSI color not rgba
    cursor_x = 0

    for h in range(height):
        for w in range(width):
            draw_char, rgba = get_pixel_func(pixels, w, h)
            skip_pixel = False
            if draw_char is not None:
                alpha = rgba[3]
                if alpha == 0:
                    skip_pixel = True       # skip any full transparent pixel
                elif alpha != 255 and bgcolor_rgba is not None:
                    rgba = alpha_blend(rgba, bgcolor_rgba)

            if not skip_pixel:
                this_pixel_str = ""
                rgb = rgba[:3]
                if draw_char is None:
                    draw_char = " "
                    color = bgcolor_ANSI
                else:
                    color = getANSIcolor_for_rgb(rgb)
                    if not is_overdraw and (draw_char == " ") and \
                            (color == bgcolor_ANSI):
                        skip_pixel = True
                if not skip_pixel:
                    if len(draw_char) > 1:
                        raise ValueError(
                            "Not allowing multicharacter draw strings")
                    if cursor_x < w:
                        string += "\x1b[{0}C".format(w - cursor_x)
                        cursor_x = w
                    if draw_char == " ":
                        string += generate_ANSI_to_set_fg_bg_colors(
                            prior_fg_color, prior_bg_color, prior_fg_color,
                            color)
                        prior_bg_color = color
                    else:
                        string += generate_ANSI_to_set_fg_bg_colors(
                            prior_fg_color, prior_bg_color, color,
                            bgcolor_ANSI)
                        prior_fg_color = color
                        prior_bg_color = bgcolor_ANSI
                    string += draw_char
                    cursor_x = cursor_x + 1
        if (h + 1) != height:
            string += bgcolor_ANSI_string
            prior_bg_color = bgcolor_ANSI       # because it has been reset
            string += "\n"
            cursor_x = 0
    return string


def generate_HTML_for_image(pixels, width, height):
    string = ""
    for h in range(height):
        for w in range(width):
            rgba = pixels[w, h]
            string += ("<span style=\"color:rgba({0}, {1}, {2}, {3});\">"
                       "▇</span>").format(
                rgba[0], rgba[1], rgba[2], rgba[3] / 255.0)
        string += "\n"
    return string


def generate_grayscale_for_image(pixels, width, height, bgcolor):
    color = "MNHQ$OC?7>!:-;. "
    string = ""
    for h in range(height):
        for w in range(width):
            rgba = pixels[w, h]
            if rgba[3] != 255 and bgcolor is not None:
                rgba = alpha_blend(rgba, bgcolor)
            rgb = rgba[:3]
            string += color[int(sum(rgb) / 3.0 / 256.0 * 16)]
        string += "\n"
    return string


def load_and_resize_image(imgname, antialias, maxLen):
    from PIL import Image
    img = Image.open(imgname)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    if maxLen is not None:
        native_width, native_height = img.size
        rate = float(maxLen) / max(native_width, native_height)
        width = int(rate * native_width) * 2
        height = int(rate * native_height)
        if native_width != width or native_height != height:
            img = img.resize((width, height), Image.ANTIALIAS
                             if antialias else Image.NEAREST)
    return img


def img2txt(imgname, maxLen=35, clr='', ansi=False,
            html=False, fontSize='', bgcolor='', antialias=True):
    try:
        maxLen = float(maxLen)
    except:
        maxLen = 35.0   # default maxlen: 30px
    try:
        fontSize = int(fontSize)
    except:
        fontSize = 7
    try:
        bgcolor = HTMLColorToRGB(bgcolor) + (255, )
    except:
        bgcolor = None
    try:
        from PIL import Image
        img = load_and_resize_image(imgname, antialias, maxLen)
    except IOError:
        return "File not found: " + imgname
    except ImportError:
        return 'PIL not found.'
    reveal_type(img)