ffmpeg -framerate 10 -i %04d.png -vframes 499 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" IntuitiveGreenhouseEffect.mp4
