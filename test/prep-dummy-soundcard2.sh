cat << EOF > ~/.asoundrc
       pcm.dummy {
          type hw
          card 0
       }
       
       ctl.dummy {
          type hw
          card 0
       }
EOF