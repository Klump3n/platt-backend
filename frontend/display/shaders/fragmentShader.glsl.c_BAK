#version 300 es

// fragment shaders don't have a default precision so we need
// to pick one. mediump is a good default. It means "medium precision"
precision mediump float;

in vec4 v_color;
in float v_temp;

// we need to declare an output for the fragment shader
out vec4 outColor;

/* Definition of color palette as per http://www.dhondt.de/
 * n   r   g   b
 * 
 * 1  191   0   0
 * 2  223  64   0
 * 3  255 128   0
 * 4  255 191   0
 * 5  255 255   0
 * 6  212 234   0
 * 7  170 212   0
 * 8  127 191   0
 * 9   85 170   0
 * 10  43 149   0
 * 11   0 128   0
 * 12   0 159  26
 * 13   0 191  51
 * 14   0 223  76
 * 15   0 255 102
 * 16   0 191 128
 * 17   0 128 153
 * 18   0  64 178
 * 19   0   0 204
 * 20  64   0 230
 * 21 128   0 255
 *
 * */

float color_exp(in float temp, in float center, in float sigma){
  return exp(-(float(temp) - center)*(float(temp) - center)/(2.*sigma*sigma));
}

float blue(in float temp){
  return color_exp(temp, -200., 100.);
}

float green(in float temp){
  return color_exp(temp, 20., 200.);
}

float red(in float temp){
  return color_exp(temp, 400., 300.);
}

void main() {
  /* if (float(v_temp) > 21.0) { */
  /*   outColor.r = 1.0; */
  /*   outColor.g = 0.0; */
  /*   outColor.b = 0.0; */
  /*   outColor.a = 1.0; */
  /* } */
  /* else { */
  /*   outColor.r = 0.0; */
  /*   outColor.g = 1.0; */
  /*   outColor.b = 0.0; */
  /*   outColor.a = 1.0; */
  /* }; */

  outColor.r = red(v_temp);
  outColor.g = green(v_temp);
  outColor.b = blue(v_temp);
  outColor.a = 1.0;
  /* outColor = v_color; */
}
