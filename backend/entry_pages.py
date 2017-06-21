#!/usr/bin/env python3
"""
This generates a individual start page for every scene. It adds the scene_hash
to the webGlCanvas element.
"""

def generate_entry_page(
        scene_hash,
        with_menu=True, with_colorbar=True
):
    html_page = """
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>FemGL alpha</title>
      <link rel="stylesheet" href="menu.css" />
      <link rel="stylesheet" href="colorbar.css" />
  </head>
  <body>
    <canvas id="webGlCanvas" data-scene-hash="{}"></canvas>
    <div class="main_container">
      <div class="add_objects_button_container">
        <div class="add_objects_button" id="add_objects_button">+</div>
        <div class="add_objects_menu_container" id="add_objects_menu_container">
            <div class="add_objects_menu" id="add_objects_menu"></div>
        </div>
      </div>
      <div class="objects_container" id="objects_container"></div>
    </div>
    <div class="colorbar_container_outer">
      <div class="colorbar_container_inner">
        <div id="colorbar"></div>
      </div>
    </div>
  </body>

  <!-- Import twgl.js WebGL helper functions -->
  <!-- <script src="twgl-dist-3.x/twgl-full.min.js"></script> -->
  <script src="twgl-dist-3.x/twgl-full.js"></script>
  <script src="menu.js" onload="main()"></script>
  <script src="loadData.js"></script>
  <script src="setView.js"></script>
  <!-- <script src="setCamera.js"></script> -->
  <script src="colorbar.js"></script>
  <script src="main.js" onload="main()"></script>
</html>
    """.format(scene_hash)
    return html_page
