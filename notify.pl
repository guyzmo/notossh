##
## Put me in ~/.irssi/scripts, and then execute the following in irssi:
##
##       /load perl
##       /script load notify
##

use strict;
use Irssi;
use vars qw($VERSION %IRSSI);
use IO::Socket;

$VERSION = "0.2";
%IRSSI = (
    authors     => 'Bernard `Guyzmo` Pratz, Luke Macken, Paul W. Frields',
    contact     => 'guyzmo AT m0g DOT net, lewk@csh.rit.edu, stickster@gmail.com',
    name        => 'notify.pl',
    description => 'Use libnotify over SSH to alert user for hilighted messages',
    license     => 'GNU General Public License',
    url         => 'http://github.com/guyzmo/irssi-over-ssh-notifications',
);

sub notify {
    my ($server, $summary, $message) = @_;

    my $remote = IO::Socket::INET->new(
                        Proto    => "tcp",
                        PeerAddr => "localhost",
                        PeerPort => "4222",
                    )
                  or die "cannot connect to 4222 port at localhost";
    # ... write notifications to the socket ... #
	print $remote $summary . ": '" . $message . "'\n";
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
