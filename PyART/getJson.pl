push(@INC,"understand/scitools/bin/linux64/Perl/STI");


use Understand;
use strict;

#my ($path) = "./trainProj/";


my $dir = "./testudb/";
my @files = ();
#print $dir;
opendir DIR,$dir or die "Can not open this dir";
my @file_list =  grep { /^[^\.]/ } readdir DIR;
closedir DIR;
#print @file_list;
#$i=0
foreach (@file_list) {
	#print "$_\n";
	my $udb_dir = $dir;
	$udb_dir .= $_;
	#print "$udb_dir\n";
	my $func_info_dir = "./testJson1/";
	my $len = length($_);
	my $proj = substr($_,0,$len-4);
	#print "$proj\n";
	$func_info_dir .= $proj;
	$func_info_dir .= ".json";
	#print "$func_info_dir\n"
	(my $db, my $status) = Understand::open($udb_dir);
	if(!$db)
	{
		die "Error opening .udb database: $status\n" if $status;
	}

	my @ents = $db->ents("function ~unknown ~unresolved");


	open FILE, ">$func_info_dir";
	# print FILE "id,kind,name,file,start_line,end_line\n";

	my $i = 0;
	foreach my $ent (@ents)
	{
		my $define_ref = $ent->ref("definein");
		next unless(defined $define_ref);

		my $end_ref = $ent->ref("endby");
		next unless(defined $end_ref);

		my $id = $ent -> id();
		my $kind = $ent->kind()->longname();
		my $name = $ent->longname();
		
		my $file = $define_ref->file->longname();
		$file =~ s/\\/\//g;

		my @parameters = ();
		my @refs = $ent->refs("define");
		foreach my $ref(@refs)
		{
			if ($ref) {
				push(@parameters, $ref->ent->name());
				# print($ref->ent->name(), " ");
			}
		}
		
		my $start_line = $define_ref->line();
		my $end_line = $end_ref->line();

		

		print FILE "$name\n";
		#print FILE "\"id\":$id,\"kind\":\"$kind\",\"name\":\"$name\",\"parameters\":\"@parameters\",\"file\":\"$file\",\"start_line\":$start_line,\"end_line\":$end_line\n";
		$i++;

	}
	close(FILE);


	$db->close();
	
	
	
	
}


