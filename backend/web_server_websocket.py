#!/usr/bin/env python3
"""
The class for the WebSocket endpoint.

"""
import re
import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin
from ws4py.websocket import WebSocket

# import global variables (scene_manager)
import backend.global_settings as gloset


class SceneManagerPlugin(WebSocketPlugin):

    def start(self):
        WebSocketPlugin.start(self)
        self.bus.subscribe('websocket-add', self.websocket_add)
        self.bus.subscribe('websocket-remove', self.websocket_remove)
        self.bus.subscribe('websocket-send', self.websocket_send)

    def stop(self):
        WebSocketPlugin.stop(self)
        self.bus.unsubscribe('websocket-add', self.websocket_add)
        self.bus.unsubscribe('websocket-remove', self.websocket_remove)
        self.bus.unsubscribe('websocket-send', self.websocket_send)

    def websocket_add(self, scene_hash, websocket):
        target_scene = gloset.scene_manager.scene(scene_hash)
        target_scene.websocket_add(websocket)

        # amount = len(target_scene._websocket_list)
        # target_scene.websocket_send('There are {} clients connected'.format(amount))

    def websocket_remove(self, scene_hash, websocket):
        target_scene = gloset.scene_manager.scene(scene_hash)
        target_scene.websocket_remove(websocket)

    def websocket_send(self, scene_hash, message):
        target_scene = gloset.scene_manager.scene(scene_hash)
        target_scene.websocket_send(message)


class WebSocketHandler(WebSocket):

    def opened(self):
        # check if scene_hash has been added to the websocket
        if hasattr(self, 'scene_hash'):
            cherrypy.engine.publish('websocket-add', self.scene_hash, self)
        else:
            pass

    def closed(self, code, reason):
        # check if scene_hash has been added to the websocket
        if hasattr(self, 'scene_hash'):
            cherrypy.engine.publish('websocket-remove', self.scene_hash, self)
        else:
            pass

    # def received_message(self, message):
    #     cherrypy.engine.publish('websocket-send', self.scene_hash, message)


class WebSocketAPI(object):

    def _cp_dispatch(self, vpath):
        scene_hash = vpath.pop(0)

        if (re.search('^[0-9a-f]{40}$', scene_hash)):
            cherrypy.request.params['scene_hash'] = scene_hash
            return WebSocketSession()
        else:
            return None


class WebSocketSession:

    @cherrypy.expose
    def default(self, scene_hash):

        active_scenes = gloset.scene_manager.list_scenes()['activeScenes']

        if scene_hash in active_scenes:
            # save the scene hash
            cherrypy.request.ws_handler.scene_hash = scene_hash

        return None
