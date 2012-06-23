#!/usr/bin/perl -w

my %mp3Tags = ( 
"artist" => "--artist=",
"title" => "--song=",
"year" => "--year=",
"track" => "--track=",
"genre" => "--genre="
);

my %flacTags = (
"artist" => "--set-tag=Artist=",
"title" => "--set-tag=Title=",
"year" => "--set-tag=Date=",
"track" => "--set-tag=Tracknumber=",
"genre" => "--set-tag=Genre="
);

my @AllTags = [ "artist", "title", "year", "track", "genre" ];

sub setTag {
  my ($file, %tags) = @_;

  my $tagSet = undef;
  die "UNDEFINED FILE" if not defined $file;

  $file =~ /.*\.(\w+)$/;
  my $format = $1;
  my $debug = 1;
  print "FILE FORMAT OF $file IS $format\n" if $debug;

  my $formatString;

  if ( lc($format) eq "mp3" ) {
    $formatString = "id3tag -2 ";
    $tagSet = \%mp3Tags;
  }
  elsif ( lc($format) eq "flac" ) {
    $formatString = "metaflac ";
    $tagSet = \%flacTags;
  }
  else {
    print "Unknown format for file $file\n";
    return;
  }
 
  for my $tag (@AllTags) {
    $formatString .= qq($tagSet->{$tag}"$tags{$tag}" ) if exists $tags{$tag};
  }
  $formatString .= qq("$file");

  print "FORMATSTRING: $formatString\n";
}




foreach my $fullfile(@ARGV) {
  setTag( $fullfile ) if -f $fullfile;
}




if (0) {
foreach my $fullfile (@ARGV) {
  $_ = `basename "$fullfile"`;
  /(\d+) - (.+) - (.+) \((\d+)\)/;
  my ($track,$artist,$title,$year) = ($1,$2,$3,$4);
  
  # DEBUG
  #print "$fullfile\n\t$track $artist $title $year\n";

  my $str = qq(id3tag -2 --artist="$artist" --song="$title" --year="$year" --track="$track" "$fullfile");

  # DEBUG
  #print "STR IS $str\n";
  qx($str);
}


my %bAbbrev = (
"AT"  => "Argentine Tango",
"B"  => "Bolero",
"CC"  => "Cha Cha",
"C"  => "Cha Cha",
"ECS"  => "East Coast Swing",
"F"  => "Foxtrot",
"H"  => "Hustle",
"J"  => "Jive",
"M"  => "Mambo",
"Me"  => "Merengue",
"NC"  => "Nightclub Two Step",
"P"  => "Peabody",
"Q"  => "Quickstep",
"R"  => "Rumba",
"Sa"  => "Salsa",
"S"  => "Samba",
"T"  => "Tango",
"VW"  => "Viennese Waltz",
"W"  => "Waltz",
"WCS"  => "West Coast Swing" );


foreach my $fullfile( @ARGV) {
  $_ = `basename "$fullfile"`;
  /([A-Za-z]+)_(\S+)\.flac/;
  #print "$1 $2\n";
  if ( exists $bAbbrev{$1} ) {
    #print "$_ => $bAbbrev{$1}, $2\n";
    my $str = qq(metaflac --set-tag=Title="$2" --set-tag=Genre="$bAbbrev{$1}" "$fullfile");
    #print "$str\n";
    qx($str);
  }
  else {
    print "FAILED - $fullfile\n";
    exit(0);
  }
}
}
