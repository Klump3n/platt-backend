#version 300 es
#extension GL_OES_standard_derivatives : enable

// fragment shaders don't have a default precision so we need
// to pick one. mediump is a good default. It means "medium precision"
precision mediump float;

in vec4 v_color;
in float v_temp;
in vec3 v_bc;
in vec4 v_gl_Position;

// we need to declare an output for the fragment shader
out vec4 outColor;

/* float color_exp(in float temp, in float center, in float sigma){ */
/*   return exp(-(float(temp) - center)*(float(temp) - center)/(2.*sigma*sigma)); */
/* } */

/* float blue(in float temp){ */
/*   return color_exp(temp, -200., 100.); */
/* } */

/* float green(in float temp){ */
/*   return color_exp(temp, 20., 200.); */
/* } */

/* float red(in float temp){ */
/*   return color_exp(temp, 400., 300.); */
/* } */

/* /\* From http://codeflow.org/entries/2012/aug/02/easy-wireframe-display-with-barycentric-coordinates/ *\/ */
/* float edgeFactor(){ */
/*   vec3 d = fwidth(v_bc); */
/*   vec3 a3 = smoothstep(vec3(0.0), d*0.5, v_bc); */
/*   return min(min(a3.x, a3.y), a3.z); */
/* } */

vec3 fragmentColour(in float temp) {
  /* Definition of color palette as per http://www.dhondt.de/ */
  if (temp < 0.0f) {
    return vec3(1.0f, 1.0f, 1.0f);
  }
  else if ((temp >= 0.000000f) && (temp < 0.047619f)) {
    return vec3(0.501961f, 0.000000f, 1.000000f);
  }
  else if ((temp >= 0.047619f) && (temp < 0.095238f)) {
    return vec3(0.200000f, 0.000000f, 1.000000f);
  }
  else if ((temp >= 0.095238f) && (temp < 0.142857f)) {
    return vec3(0.000000f, 0.000000f, 0.800000f);
  }
  else if ((temp >= 0.142857f) && (temp < 0.190476f)) {
    return vec3(0.000000f, 0.250980f, 0.698039f);
  }
  else if ((temp >= 0.190476f) && (temp < 0.238095f)) {
    return vec3(0.000000f, 0.501961f, 0.600000f);
  }
  else if ((temp >= 0.238095f) && (temp < 0.285714f)) {
    return vec3(0.000000f, 0.749020f, 0.501961f);
  }
  else if ((temp >= 0.285714f) && (temp < 0.333333f)) {
    return vec3(0.000000f, 1.000000f, 0.400000f);
  }
  else if ((temp >= 0.333333f) && (temp < 0.380952f)) {
    return vec3(0.000000f, 0.874510f, 0.298039f);
  }
  else if ((temp >= 0.380952f) && (temp < 0.428571f)) {
    return vec3(0.000000f, 0.749020f, 0.200000f);
  }
  else if ((temp >= 0.428571f) && (temp < 0.476190f)) {
    return vec3(0.000000f, 0.623529f, 0.101961f);
  }
  else if ((temp >= 0.476190f) && (temp < 0.523810f)) {
    return vec3(0.000000f, 0.501961f, 0.000000f);
  }
  else if ((temp >= 0.523810f) && (temp < 0.571429f)) {
    return vec3(0.168627f, 0.584314f, 0.000000f);
  }
  else if ((temp >= 0.571429f) && (temp < 0.619048f)) {
    return vec3(0.333333f, 0.666667f, 0.000000f);
  }
  else if ((temp >= 0.619048f) && (temp < 0.666667f)) {
    return vec3(0.498039f, 0.749020f, 0.000000f);
  }
  else if ((temp >= 0.666667f) && (temp < 0.714286f)) {
    return vec3(0.666667f, 0.831373f, 0.000000f);
  }
  else if ((temp >= 0.714286f) && (temp < 0.761905f)) {
    return vec3(0.831373f, 0.917647f, 0.000000f);
  }
  else if ((temp >= 0.761905f) && (temp < 0.809524f)) {
    return vec3(1.000000f, 1.000000f, 0.000000f);
  }
  else if ((temp >= 0.809524f) && (temp < 0.857143f)) {
    return vec3(1.000000f, 0.749020f, 0.000000f);
  }
  else if ((temp >= 0.857143f) && (temp < 0.904762f)) {
    return vec3(1.000000f, 0.501961f, 0.000000f);
  }
  else if ((temp >= 0.904762f) && (temp < 0.952381f)) {
    return vec3(0.874510f, 0.250980f, 0.000000f);
  }
  else if ((temp >= 0.952381f) && (temp < 1.000000f)) {
    return vec3(0.749020f, 0.000000f, 0.000000f);
  }
  else {
    return vec3(1.0f, 1.0f, 1.0f);
  }
}

void main() {
  vec3 nodeColour = fragmentColour(v_temp);
  outColor = vec4(nodeColour, 1.0);

  /* outColor = vec4(0.0, 0.0, 0.0, 1.0); */




  /* vec3 dbc = fwidth(v_bc); */
  /* if (any(greaterThan(dbc, vec3(0.5)))) { */
  /*   outColor = vec4(vec3(red(v_temp), green(v_temp), blue(v_temp)), 1.0); */
  /* } */
  /* else { */
  /*   vec3 a3 = smoothstep(vec3(0.0), dbc*1.5, v_bc); */
  /*   float edgeFactor = min(min(a3.x, a3.y), a3.z); */
  /*   vec3 outval = mix(vec3(0.0), vec3(red(v_temp), green(v_temp), blue(v_temp)), edgeFactor); */
  /*   outColor = vec4(outval, 1.0); */
  /*   /\* outColor = vec4(vec3(red(v_temp), green(v_temp), blue(v_temp)), 1.0); *\/ */
  /* } */

  /* vec3 fadetest = vec3(0.0) + (vec3(red(v_temp), green(v_temp), blue(v_temp)) - vec3(0.0))*edgeFactor(); */
  /* vec3 outval = mix(vec3(0.0), vec3(red(v_temp), green(v_temp), blue(v_temp)), .5*edgeFactor()); */
  /* outColor = vec4(fadetest, 1.0); */
  /* outColor = vec4(0.0, 0.0, 0.0, (1.0-edgeFactor())); */



  /* vec3 outval = mix(vec3(0.0), vec3(red(v_temp), green(v_temp), blue(v_temp)), edgeFactor()); */
  /* outColor = vec4(outval, 1.0); */

  /* vec3 rgb = vec3(red(v_temp), green(v_temp), blue(v_temp)); */
  /* vec3 oneoverz_rgb = 1.0*(1.0 - edgeFactor()) * vec3(red(v_temp), green(v_temp), blue(v_temp)); */
  /* outColor = vec4(rgb - oneoverz_rgb, 1.0); */

  /* outColor = vec4(0.0, 0.0, 0.0, (1.0-edgeFactor())*0.95); */
}
