#version 300 es

// an attribute is an input (in) to a vertex shader.
// It will receive data from a buffer
in vec3 a_line_data;

uniform mat4 u_transform;

// all shaders have a main function
void main() {

  gl_Position = u_transform * vec4(a_line_data, 1);

}
