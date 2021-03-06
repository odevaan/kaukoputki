#!/usr/bin/perl
# convert  astorb.txt to 2 .edb files.
# Usage: [-f] <base>
#   if -f then use ftp to get the script from lowell, else read it from stdin.
#   <base> is a prefix used in naming the generated .edb files.
# Two files are created:
#   <base>.edb contains only those asteroids which might ever be brighter
#      than $dimmag (set below);
#   <base>_dim.edb contains the remaining asteroids.
#
# astorb is a set of elements for 30k+ asteroids maintained by Lowell
# Observatory. See ftp://ftp.lowell.edu/pub/elgb/astorb.html. From the
# Acknowledgments section of same:
#   The research and computing needed to generate astorb.dat were funded
#   principally by NASA grant NAGW-1470, and in part by the Lowell Observatory
#   endowment. astorb.dat may be freely used, copied, and transmitted provided
#   attribution to Dr. Edward Bowell and the aforementioned funding sources is
#   made. 
#
# Elwood Downey
#  2 Jul 1996 first draft
# 10 Oct 1996 update for field 18 change; add notion of astorb_dim.edb
#  1 Sep 1997 change name to asteroids*.edb for OCAAS
# 10 Mar 1999 update for field 1 change
#  5 Apr 2000 change args to match mpcorb.pl
#  6 Oct 2000: add -f

# grab RCS version
$ver = '$Revision: 1.8 $';
$ver =~ s/\$//g;

# setup cutoff mag
$dimmag = 13;			# dimmest mag to be saved in "bright" file

# set site and file in case of -f
$ORBSITE = "ftp.lowell.edu";
$ORBFTPDIR = "/pub/elgb";
$ORBFILE = "astorb.dat";
$ORBGZFILE = "astorb.dat.gz";

# immediate output
$| = 1;

# crack args.
# when thru here $fnbase is prefix name and $srcfd is handle to $ORBFILE.
if (@ARGV == 2) {
    &usage() unless @ARGV[0] eq "-f";
    &fetch();
    open SRCFD, $ORBFILE or die "$ORBFILE: $?\n";
    $srcfd = SRCFD;
    $fnbase = $ARGV[1];
} elsif (@ARGV != 1) {
    &usage();
} else {
    &usage() if @ARGV[0] =~ /^-/;
    $srcfd = STDIN;
    $fnbase = $ARGV[0];
}

# create output files prefixed with $fnbase
$brtfn = "$fnbase.edb";		# name of file for bright asteroids
open BRT, ">$brtfn" or die "Can not create $brtfn\n";
$dimfn = "$fnbase"."_dim.edb";	# name of file for dim asteroids
open DIM, ">$dimfn" or die "Can not create $dimfn\n";
print "Creating $brtfn and $dimfn..\n";

# build some common boilerplate
($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime;
$year += 1900;
$mon += 1;
$from = "# Data From ftp://ftp.lowell.edu/pub/elgb/astorb.dat.gz\n";
$what = "# Generated by astorb2edb.pl $ver, (c) 2000 Elwood Downey\n";
$when = "# Processed $year-$mon-$mday $hour:$min:$sec UTC\n";

# add boilerplate to each file
print BRT "# Asteroids ever brighter than $dimmag.\n";
print BRT $from;
print BRT $what;
print BRT $when;
print DIM "# Asteroids never brighter than $dimmag.\n";
print DIM $from;
print DIM $what;
print DIM $when;

# column table, from sample FORTRAN format
# 1..5		A5,1X,
# 7..24		A18,1X,
# 26..40	A15,1X,
# 42..46	A5,1X,
# 48..52	F5.2,1X,
# 54..57	A4,1X,
# 59..63	A5,1X,
# 65..68	A4, 1X,
# 70..93	6I4,1X,
# 95..104	2I5,1X,
# 106..109 110..111 112..113  I4,2I2.2,1X,
# 115..124 126..135 137..146 3(F10.6,1X),
# 148..156 	F9.6,1X,
# 158..167 	F10.8, 1X,
# 169..180 	F12.8,1X,
# 182..185 186..187 188..189 I4,2I2.2,1X,

# process each astorb.dat entry
while (<$srcfd>) {
    # build the name
    $nmbr = &s(1,5) + 0;
    $name = &s(7,24);
    $name =~ s/^ *//;
    $name =~ s/ *$//;

    # gather the orbital params
    $i = &s(148,156) + 0;
    $O = &s(137,146) + 0;
    $o = &s(126,135) + 0;
    $a = &s(169,180) + 0;
    $e = &s(158,167) + 0;
    $M = &s(115,124) + 0;
    $H = &s(42,46) + 0;
    $G = &s(48,52) + 0;
    $TM = &s(110,111) + 0;
    $TD = &s(112,113) + 0;
    $TY = &s(106,109) + 0;

    # decide whether it's ever bright
    $per = $a*(1 - $e);
    $aph = $a*(1 + $e);
    if ($per < 1.1 && $aph > .9) {
	$fd = BRT;	# might be in the back yard some day :-)
    } else {
	$maxmag = $H + 5*&log10($per*&absv($per-1));
	$fd = $maxmag > $dimmag ? DIM : BRT;
    }

    # print
    print $fd "$nmbr " if ($nmbr != 0);
    print $fd "$name";
    print $fd ",e,$i,$O,$o,$a,0,$e,$M,$TM/$TD/$TY,2000.0,$H,$G\n";
}

# remove fetched file, if any
unlink $ORBFILE;
unlink $ORBGZFILE;

exit 0;

# like substr($_,first,last), but one-based.
sub s {
    substr ($_, $_[0]-1, $_[1]-$_[0]+1);
}

# return log base 10
sub log10 {
    .43429*log($_[0]);
}

# return absolute value
sub absv {
    $_[0] < 0 ? -$_[0] : $_[0];
}

# print usage message then die
sub usage
{
    my $base = $0;
    $base =~ s#.*/##;
    print "Usage: $base [-f] <base>\n";
    print "$ver\n";
    print "Purpose: convert $ORBFILE to 2 .edb files.\n";
    print "Options:\n";
    print "  -f: first ftp $ORBFILE from $ORBSITE, else read from stdin\n";
    print "Creates two files:\n";
    print "  <base>.edb:     all asteroids ever brighter than $dimmag\n";
    print "  <base>_dim.edb: all asteroids never brighter than $dimmag\n";

    exit 1;
}

# get and explode the data
sub fetch
{
    # transfer
    print "Getting $ORBFTPDIR/$ORBGZFILE from $ORBSITE...\n";
    open ftp, "|ftp -n $ORBSITE" or die "Can not ftp $ORBSITE";
    print ftp "user anonymous xephem\@clearskyinstitute.com\n";
    print ftp "binary\n";
    print ftp "cd $ORBFTPDIR\n";
    print ftp "get $ORBGZFILE\n";
    close ftp;

    # explode
    print "Decompressing $ORBGZFILE ...\n";
    $gunzip = "gunzip";
    !system "$gunzip < $ORBGZFILE > $ORBFILE" or die "$gunzip failed\n";
    -s $ORBFILE or die "$ORBFILE: failed to create from $gunzip $ORBGZFILE\n";
}

# For RCS Only -- Do Not Edit
# @(#) $RCSfile: astorb2edb.pl,v $ $Date: 2001/08/15 05:35:15 $ $Revision: 1.8 $ $Name:  $
