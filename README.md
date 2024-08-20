# Jukebox
This was a take home project for an interview process.

## Project Description

We would like to build a jukebox program.

The jukebox stores multiple albums, each of which contains multiple songs. Users should be able to select songs with a five-character identifier: a two-digit ID for the album, a hyphen, and a two-digit ID for the song. For example, the fourth song on the first album should be identified as "01-04."

As users select songs, the songs should be added to a play queue. Songs should be played in the order they are selected.

Adding a song to the queue costs one credit. Credits are purchased by the user in whole-number dollar amounts. $1 dollar purchases 3 credits; $2 purchases 7 credits; and $5 purchases 18 credits. Any positive whole number should be accepted; for example, $8 should purchase 28 credits ($5 + $2 + $1) while $10 should purchase 36 credits ($5 + $5).

The jukebox should be able to:

* List available albums and songs with their appopropriate IDs;
* Accept dollar amounts and credit the user appropriately;
* Add new songs to the queue;
* Report the song currently playing; and
* Report the next song to play.

While not part of the current requirements, we'd also like to eventually build an HTTP API for the jukebox. While you don't need to build it, please give some thought to how you'd implement it and be prepared to discuss a potential design.

We have provided sample data for albums and songs -- use it if helps you.

## Design Decisions and Assumptions
Assumed we would want to make this with microservices, and make it extendable.

The various components are described in more detail below.  Some of the components could easily be combined.

I am using environment variables for configuration options.

Interfaces/Protocols are defined where they are used, mostly.  The exception is the factories (from_config), but those interfaces are a contract for what methods will be available in the objects.

While the current design makes different objects for each component, a number of them could be implemented using a single database for persistant storage.

Pagination cursors are simply a string, but would probably be switched to an interface.  Need more detail.

#### Discography Repository:
This stores the available albums and their associated tracks.  It's used by the service and player to get information about songs.  This is most likely a database somewhere, so I componentized it.

#### Track Queue:
The track queue simply stores the queue of tracks users have placed in it.  The example implementation is an in memory queue, but this could easily be swapped out with more persistant storage.

#### Audio Player:
I'm assuming this another external service.  Though it could be running locally in a subprocess.

The, quite big, assumption here is that the audio player would read from the queue.  This may not be the case.

#### Credit Repository
While very small in this example the credit storage component would be some type of storage so that credits wouldn't be lost in the case of an outage.

#### Domain:
The domain handles just the businessy logic, and ties a number of services together.

I originally had credits associated to users, but that's a more advanced jukebox system, not the classic style.


## HTTP API
Standard JSON RESTful API should be acceptable.  But if this is purely a system to system interface an RPC API should be considered.  So assuming we're using JSON RESTful:

Basic layout of the API is available in the swagger.yml file.

