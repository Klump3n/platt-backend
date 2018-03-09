#version 300 es

// fragment shaders don't have a default precision so we need
// to pick one. mediump is a good default. It means "medium precision"
precision mediump float;

in vec4 v_color;
in float v_field;
/* in vec3 v_bc; */
in vec4 v_gl_Position;

// we need to declare an output for the fragment shader
out vec4 outColor;

vec3 fragmentColour(in float field_value) {
  /* Definition of color palette as per http://www.dhondt.de/ */
  if (field_value < 0.0f) {
    return vec3(1.0f, 1.0f, 1.0f);
  }
  else if ((field_value >= 0.000000f) && (field_value < 0.047619f)) {
    return vec3(0.501961f, 0.000000f, 1.000000f);
  }
  else if ((field_value >= 0.047619f) && (field_value < 0.095238f)) {
    return vec3(0.200000f, 0.000000f, 1.000000f);
  }
  else if ((field_value >= 0.095238f) && (field_value < 0.142857f)) {
    return vec3(0.000000f, 0.000000f, 0.800000f);
  }
  else if ((field_value >= 0.142857f) && (field_value < 0.190476f)) {
    return vec3(0.000000f, 0.250980f, 0.698039f);
  }
  else if ((field_value >= 0.190476f) && (field_value < 0.238095f)) {
    return vec3(0.000000f, 0.501961f, 0.600000f);
  }
  else if ((field_value >= 0.238095f) && (field_value < 0.285714f)) {
    return vec3(0.000000f, 0.749020f, 0.501961f);
  }
  else if ((field_value >= 0.285714f) && (field_value < 0.333333f)) {
    return vec3(0.000000f, 1.000000f, 0.400000f);
  }
  else if ((field_value >= 0.333333f) && (field_value < 0.380952f)) {
    return vec3(0.000000f, 0.874510f, 0.298039f);
  }
  else if ((field_value >= 0.380952f) && (field_value < 0.428571f)) {
    return vec3(0.000000f, 0.749020f, 0.200000f);
  }
  else if ((field_value >= 0.428571f) && (field_value < 0.476190f)) {
    return vec3(0.000000f, 0.623529f, 0.101961f);
  }
  else if ((field_value >= 0.476190f) && (field_value < 0.523810f)) {
    return vec3(0.000000f, 0.501961f, 0.000000f);
  }
  else if ((field_value >= 0.523810f) && (field_value < 0.571429f)) {
    return vec3(0.168627f, 0.584314f, 0.000000f);
  }
  else if ((field_value >= 0.571429f) && (field_value < 0.619048f)) {
    return vec3(0.333333f, 0.666667f, 0.000000f);
  }
  else if ((field_value >= 0.619048f) && (field_value < 0.666667f)) {
    return vec3(0.498039f, 0.749020f, 0.000000f);
  }
  else if ((field_value >= 0.666667f) && (field_value < 0.714286f)) {
    return vec3(0.666667f, 0.831373f, 0.000000f);
  }
  else if ((field_value >= 0.714286f) && (field_value < 0.761905f)) {
    return vec3(0.831373f, 0.917647f, 0.000000f);
  }
  else if ((field_value >= 0.761905f) && (field_value < 0.809524f)) {
    return vec3(1.000000f, 1.000000f, 0.000000f);
  }
  else if ((field_value >= 0.809524f) && (field_value < 0.857143f)) {
    return vec3(1.000000f, 0.749020f, 0.000000f);
  }
  else if ((field_value >= 0.857143f) && (field_value < 0.904762f)) {
    return vec3(1.000000f, 0.501961f, 0.000000f);
  }
  else if ((field_value >= 0.904762f) && (field_value < 0.952381f)) {
    return vec3(0.874510f, 0.250980f, 0.000000f);
  }
  else if ((field_value >= 0.952381f) && (field_value < 1.000000f)) {
    return vec3(0.749020f, 0.000000f, 0.000000f);
  }
  else {
    return vec3(1.0f, 1.0f, 1.0f);
  }
}

void main() {
  vec3 nodeColour = fragmentColour(v_field);
  outColor = vec4(nodeColour, 1.0);

  /* outColor = vec4(0.0, 0.0, 0.0, 1.0); */
}
