##
## Put me in ~/.irssi/scripts, and then execute the following in irssi:
##
##       /load perl
##       /script load notify
##

use strict;
use Irssi;
use vars qw($VERSION %IRSSI);
#use IO::Socket;

$VERSION = "0.01";
%IRSSI = (
    authors     => 'Luke Macken, Paul W. Frields',
    contact     => 'lewk@csh.rit.edu, stickster@gmail.com',
    name        => 'notify.pl',
    description => 'Use libnotify to alert user to hilighted messages',
    license     => 'GNU General Public License',
    url         => 'http://lewk.org/log/code/irssi-notify',
);

sub send_notification {
#    $remote = IO::Socket::INET->new(
#                        Proto    => "tcp",
#                        PeerAddr => "localhost",
#                        PeerPort => "4222",
#                    )
#                  or die "cannot connect to daytime port at localhost";
#   # ... write notifications to the socket ... #
#}

sub notify {
    my ($server, $summary, $message) = @_;

    # Make the message entity-safe
    $message =~ s/&/&amp;/g; # That could have been done better.
    $message =~ s/</&lt;/g;
    $message =~ s/>/&gt;/g;
    $message =~ s/'/&apos;/g;
    $summary =~ s/&/&amp;/g; # That could have been done better.
    $summary =~ s/</&lt;/g;
    $summary =~ s/>/&gt;/g;
    $summary =~ s/'/&apos;/g;

    my $cmd = "EXEC - notify-send " .
	$summary . ": '" . $message . "'";

    $server->command($cmd);
}
 
sub print_text_notify {
    my ($dest, $text, $stripped) = @_;
    my $server = $dest->{server};

    return if (!$server || !($dest->{level} & MSGLEVEL_HILIGHT));
    my $sender = $stripped;
    $sender =~ s/^\<.([^\>]+)\>.+/\1/ ;
    my $summary = $sender . "@" . $dest->{server}->{tag} . $dest->{target};

    $stripped =~ s/^\<.[^\>]+\>.// ;
    notify($server, $summary, $stripped);
}

sub message_private_notify {
    my ($server, $msg, $nick, $address) = @_;

    return if (!$server);
    notify($server, "PM from ".$nick, $msg);
}

sub dcc_request_notify {
    my ($dcc, $sendaddr) = @_;
    my $server = $dcc->{server};

    return if (!$dcc);
    notify($server, "DCC ".$dcc->{type}." request", $dcc->{nick});
}

Irssi::signal_add('print text', 'print_text_notify');
Irssi::signal_add('message private', 'message_private_notify');
Irssi::signal_add('dcc request', 'dcc_request_notify');
