#version 300 es

// an attribute is an input (in) to a vertex shader.
// It will receive data from a buffer
in vec3 a_position;
/* in vec4 a_color; */

in vec3 a_bc;
out vec3 v_bc;

in float a_temp;
out float v_temp;

out vec4 v_gl_Position;

uniform mat4 u_transform;

// all shaders have a main function
void main() {

  // gl_Position is a special variable a vertex shader
  // is responsible for setting

  /* gl_Position = a_position; */
  gl_Position = u_transform * vec4(a_position, 1);

  v_gl_Position = gl_Position;

  v_temp = a_temp;
  v_bc = a_bc;

}
