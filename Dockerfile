FROM blendergrid/blender

COPY . /sidar

WORKDIR /sidar

RUN /usr/local/blender/blender -b --python /sidar/init.py

#ENTRYPOINT ["/usr/local/blender/blender" "-b" "-noaudio"]
ENTRYPOINT ["/bin/bash"] 

#CMD ["--version"]