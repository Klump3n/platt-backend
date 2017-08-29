#!/usr/bin/env python3

# Copyright (C) 2017 Matthias Plock <matthias.plock@bam.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Contains functions for generating taylored index.html files.
"""

# The main html body
HTML = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>FemGL alpha</title>
      <link rel="stylesheet" href="main.css" />
      {html_css_overlay}
      {html_css_menu}
      {html_css_colorbar}
  </head>
  <body>
    <!-- The canvas element for displaying something via WebGL. Never
	       tried anything else, maybe it also works in a <p>? -->
    <canvas id="webGlCanvas" data-scene-hash="{scene_hash}"></canvas>
    {html_body_overlay}
    {html_body_menu}
    {html_body_colorbar}
  </body>

  <!-- Import twgl.js WebGL helper functions -->
  <!-- <script src="twgl-dist-3.x/twgl-full.min.js"></script> -->
  <script src="twgl-dist-3.x/twgl-full.js"></script>
  {html_script_menu}
  <script src="loadData.js"></script>
  <script src="setView.js"></script>
  {html_script_colorbar}
  <script src="main.js" onload="main()"></script>
</html>
"""

# The css entries for the menu, the colorbar and the overlay
CSS_OVERLAY = """
      <link rel="stylesheet" href="overlay.css" />
"""
CSS_MENU = """
      <link rel="stylesheet" href="menu.css" />
"""
CSS_COLORBAR = """
      <link rel="stylesheet" href="colorbar.css" />
"""

# Divs for menu, colorbar and overlay
BODY_OVERLAY = """
    <div class="overlay">{message}</div>
"""
BODY_MENU = """
    <div class="main_container">
      <div class="add_objects_button_container">
        <div class="add_objects_button" id="add_objects_button">+</div>
        <div class="add_objects_menu_container" id="add_objects_menu_container">
            <div class="add_objects_menu" id="add_objects_menu"></div>
        </div>
      </div>
      <div class="objects_container" id="objects_container"></div> <!-- The menus will be dropped here. -->
    </div>
"""
BODY_COLORBAR = """
    <!-- Colorbar stuff -->
    <div class="colorbar_container_outer">
      <div class="colorbar_container_inner">
        <div id="colorbar"></div>
      </div>
    </div>
    <!-- Colorbar stuff ends -->
"""

# Scripts to load for menu and colorbar
SCRIPT_MENU = """
  <script src="menu.js" onload="main()"></script>
"""
SCRIPT_COLORBAR = """
  <script src="colorbar.js"></script>
"""


def make_index(
        scene_hash="",
        with_menu=True, with_colorbar=True,
        overlay_message=None
):
    """
    Generate a string that we can return to the browser, so it knows what it has
    to load.
    """

    # Initialise strings
    css_overlay_string = ""
    css_menu_string = ""
    css_colorbar_string = ""
    body_overlay_string = ""
    body_menu_string = ""
    body_colorbar_string = ""
    script_menu_string = ""
    script_colorbar_string = ""

    if overlay_message is not None:
        css_overlay_string = CSS_OVERLAY
        body_overlay_string = BODY_OVERLAY.format(message=overlay_message)

    if with_menu:
        css_menu_string = CSS_MENU
        body_menu_string = BODY_MENU
        script_menu_string = SCRIPT_MENU

    if with_colorbar:
        css_colorbar_string = CSS_COLORBAR
        body_colorbar_string = BODY_COLORBAR
        script_colorbar_string = SCRIPT_COLORBAR

    # Format the html string
    index_file = HTML.format(
        scene_hash=scene_hash,

        html_css_overlay=css_overlay_string,
        html_css_menu=css_menu_string,
        html_css_colorbar=css_colorbar_string,

        html_body_overlay=body_overlay_string,
        html_body_menu=body_menu_string,
        html_body_colorbar=body_colorbar_string,

        html_script_menu=script_menu_string,
        html_script_colorbar=script_colorbar_string
    )

    return index_file


if __name__ == '__main__':
    """
    In case we want to test.
    """
    print(make_index())
