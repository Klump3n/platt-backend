#!/usr/bin/env python3
"""
The class for the WebSocket endpoint.

Handles adding and removing WebSocket instances to and from a scene as well as
sending data to all connected instances of a scene.

The WebSocket connected tells the connected clients when and what to update.
When the orientation of a dataset changes it tells the client to update the
orientation, when the geometry or field change it sends the new hashes of
geometry and field for reference.

Maybe later everything can be transmitted via WebSocket, but for now only
small amounts of data are transmitted this way.

"""
import re
import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin
from ws4py.websocket import WebSocket

# import global variables (scene_manager)
import backend.global_settings as gloset


class SceneManagerPlugin(WebSocketPlugin):
    """
    The WebSocket plugin added to the servers bus.

    """
    def start(self):
        """
        Start the websocket plugin and add (subscribe) routines to add, remove
        or send to a client.

        """
        WebSocketPlugin.start(self)
        self.bus.subscribe('websocket-add', self.websocket_add)
        self.bus.subscribe('websocket-remove', self.websocket_remove)
        self.bus.subscribe('websocket-send', self.websocket_send)

    def stop(self):
        """
        Stop the websocket plugin and remove (unsubscribe) the routines to add,
        remove or send to the client.

        """
        WebSocketPlugin.stop(self)
        self.bus.unsubscribe('websocket-add', self.websocket_add)
        self.bus.unsubscribe('websocket-remove', self.websocket_remove)
        self.bus.unsubscribe('websocket-send', self.websocket_send)

    def websocket_add(self, scene_hash, websocket):
        """
        Add a websocket connection to a scene.

        Args:
         scene_hash (str): The hash of the scene to which we want to append a
          websock connection.
         websocket (ws4py.websocket.WebSocket): The WebSocket instance that
          connects to the scene.

        """
        target_scene = gloset.scene_manager.scene(scene_hash)
        target_scene.websocket_add(websocket)

        # amount = len(target_scene._websocket_list)
        # target_scene.websocket_send('There are {} clients connected'.format(amount))

    def websocket_remove(self, scene_hash, websocket):
        """
        Remove a websocket connection from a scene.

        Args:
         scene_hash (str): The hash of the scene from which we want to remove a
          websock connection.
         websocket (ws4py.websocket.WebSocket): The WebSocket instance that
          connected to the scene.

        """
        target_scene = gloset.scene_manager.scene(scene_hash)
        target_scene.websocket_remove(websocket)

    def websocket_send(self, scene_hash, message):
        """
        Send a message to all the WebSocket instances that connect to the
        scene.

        Args:
         scene_hash (str): The hash of the scene to which we want to send a
          message.
         message (JSON parsable object): Something we want to transmit to all
          the connected WebSocket instances. Must be parsable by json.dumps(),
          so strings, dicts, arrays and so on.

        """
        target_scene = gloset.scene_manager.scene(scene_hash)
        target_scene.websocket_send(message)


class WebSocketHandler(WebSocket):
    """
    Handler for the WebSocket connections.

    Takes care of adding and removing websocket instances to a scene.

    """
    def opened(self):
        """
        Add a WebSocket instance to a scene when a websocket is opened.

        """
        # check if scene_hash has been added to the websocket
        if hasattr(self, 'scene_hash'):
            cherrypy.engine.publish('websocket-add', self.scene_hash, self)
        else:
            pass

    def closed(self, code, reason):
        """
        Remove a WebSocket instance from a scene when the socket is closed.

        """
        # check if scene_hash has been added to the websocket
        if hasattr(self, 'scene_hash'):
            cherrypy.engine.publish('websocket-remove', self.scene_hash, self)
        else:
            pass

    # # A hook for receiving messages from the client. Maybe used later
    # def received_message(self, message):
    #     cherrypy.engine.publish('websocket-send', self.scene_hash, message)


class WebSocketAPI(object):
    """
    The app for WebSocket support. Essentially just dispatches urls.

    """
    def _cp_dispatch(self, vpath):
        """
        The dispatcher method for calling .../websocket/(#scene_hash)

        Strips the first argument from the vpath. Checks if that argument is
        in the form of a sha1 hash. If it is, returns a WebSocketSession, else
        returns None.

        Args:
         vpath (list): A list of url segments after .../websocket/

        """
        scene_hash = vpath.pop(0)

        if (re.search('^[0-9a-f]{40}$', scene_hash)):
            cherrypy.request.params['scene_hash'] = scene_hash
            return WebSocketSession()
        else:
            return None


class WebSocketSession:
    """
    The dispatched WebSocketSession.

    Exposes one default page that gets called with the scene_hash.

    """
    @cherrypy.expose
    def default(self, scene_hash):
        """
        The only method that gets exposed.

        Compares the scene_hash with the existing scenes on the server. If the
        scene_hash is found we attach a WebSocketHandler and add the scene_hash
        to the handler.

        Args:
         scene_hash (str): The hash of the scene we want to append.

        """
        active_scenes = gloset.scene_manager.list_scenes()['activeScenes']

        if scene_hash in active_scenes:
            # save the scene hash
            cherrypy.request.ws_handler.scene_hash = scene_hash

        return None
