#version 300 es

// an attribute is an input (in) to a vertex shader.
// It will receive data from a buffer
in vec3 a_model_edges;

uniform mat4 u_transform;

// all shaders have a main function
void main() {

  gl_Position = u_transform * vec4(a_model_edges, 1);

}
