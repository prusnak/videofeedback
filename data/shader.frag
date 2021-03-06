uniform sampler2D tex;
uniform sampler2D map;
uniform int usecolormap;
uniform int negative;
uniform float randomness;
uniform float noise_level;
uniform float desaturate_level;
uniform float threshold_level;
uniform float quantize_level;
uniform float emboss_level;
uniform float separation_level;
uniform float pixelate_level;
uniform float hue_level;

float random(vec2 p)
{
    const vec2 r = vec2(23.1406926327792690, 2.6651441426902251);
    return fract(cos(mod(123456789.0, 1E-7 + 256.0 * dot(p,r) + randomness)));
}

void main()
{
    vec2 texXY = gl_TexCoord[0].xy;

    if (pixelate_level > 0.0) {
        texXY *= 100.0;
        texXY = vec2(floor(texXY.x / pixelate_level / 5.0) * pixelate_level * 5.0, floor(texXY.y / pixelate_level / 5.0 ) * pixelate_level * 5.0);
        texXY /= 100.0;
    }

    vec3 color = vec3(
        texture2D(tex, texXY - vec2(0.1 * separation_level, 0.0)).r,
        texture2D(tex, texXY).g,
        texture2D(tex, texXY + vec2(0.1 * separation_level, 0.0)).b);
    float luma = color.r * 0.2126 + color.g * 0.7152 + color.b * 0.0722;

    // set luma when using colormap
    if (usecolormap > 0) {
        color = vec3(luma);
    }

    // use threshold
    if (threshold_level > 0.0) {
        if (luma >= (1.0 - threshold_level))
            color = vec3(1.0);
        else
            color = vec3(0.0);
    }

    // use quantize
    if (quantize_level > 0.0) {
        float ql = (1.0 - quantize_level) * 5.0 + 1.0;
        float r = floor(color.r * (ql + 1.0)) / ql;
        float g = floor(color.g * (ql + 1.0)) / ql;
        float b = floor(color.b * (ql + 1.0)) / ql;
        color = vec3(r, g, b);
    }

    // use emboss
    if (emboss_level > 0.0) {
        float el = emboss_level / 100.0;
        vec3 c = vec3(0.5) + texture2D(tex, texXY - el).rgb * 2.0 - texture2D(tex, texXY + el).rgb * 2.0;
        color = vec3((c.r + c.g + c.b) / 3.0);
    }

    // apply negative
    if (negative > 0) {
        color = vec3(1.0) - color;
    }

    // apply colormap if needed
    if (usecolormap > 0) {
        color = texture2D(map, vec2(color.r, 0)).rgb;
    }

    // apply desaturate
    if (desaturate_level > 0.0) {
        color = color.rgb * (1.0 - desaturate_level) + vec3(luma) * desaturate_level;
    }

    // apply noise
    if (noise_level > 0.0) {
        color = color.rgb * (1.0 - noise_level) + vec3(random(texXY)) * noise_level;
    }

    // apply hue (hack)
    if (hue_level > 0.0) {
        color = vec3( color.r * (1.0 - hue_level) + color.g * hue_level, color.g * (1.0 - hue_level) + color.b * hue_level, color.b * (1.0 - hue_level) + color.r * hue_level );
    }
    if (hue_level < 0.0) {
        color = vec3( color.r * (1.0 + hue_level) - color.b * hue_level, color.g * (1.0 + hue_level) - color.r * hue_level, color.b * (1.0 + hue_level) - color.g * hue_level );
    }

    // fill in result
    gl_FragColor.rgb = color;
}
