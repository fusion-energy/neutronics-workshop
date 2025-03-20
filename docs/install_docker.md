# Install with Docker

There are video tutorials for this section which accompany the step by step
instructions below.

- Ubuntu installation video :point_right: <p align="center"><a href="https://youtu.be/qJLmt_dAaC0" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114008054-c9cb7e80-9859-11eb-8e07-32e95c600667.png" height="70" /></a></p>
- Windows installation video :point_right: <p align="center"><a href="https://youtu.be/1MUYgjEQeIA" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114008108-d3ed7d00-9859-11eb-8bb5-0c19ce775015.png" height="70" /></a></p>
- Mac installation video :point_right: <p align="center"><a href="https://youtu.be/jUMY-cEILcw" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114172031-05834880-992d-11eb-8277-5a6cda2b5e12.png" height="70" /></a></p>

1. Install Docker CE for
[Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/),
[Mac OS](https://store.docker.com/editions/community/docker-ce-desktop-mac), or
[Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows),
including the part where you enable docker use as a non-root user. 

2. Pull the docker image from the store by typing the following command in a
terminal window, or Windows users might prefer PowerShell.

    ```docker pull ghcr.io/fusion-energy/neutronics-workshop```

    <details>
      <summary><b>Expand</b> - Having permission denied errors?</summary>
        <pre><code class="language-html">
        If you are running the command from Linux or Ubuntu terminal and getting permission denied messages back.
        Try running the same command with with elevated user permissions by adding sudo at the front.
        sudo docker pull ghcr.io/fusion-energy/neutronics-workshop
        Then enter your password when prompted.
        </code></pre>
    </details>

3. Now that you have the docker image you can enable graphics linking between
your os and docker, and then run the docker container by typing the following
commands in a terminal window.

    ```docker run -p 8888:8888 ghcr.io/fusion-energy/neutronics-workshop```

    <details>
      <summary><b>Expand</b> - Having permission denied errors?</summary>
        <pre><code class="language-html">
        If you are running the command from Linux or Ubuntu terminal and getting permission denied messages back.
        Try running the same command with elevated user permissions by adding sudo at the front.
        sudo docker run -p 8888:8888 ghcr.io/fusion-energy/neutronics-workshop
        Then enter your password when prompted.
        </code></pre>
    </details>

4. A URL should be displayed in the terminal and can now be opened in the
internet browser of your choice. Select and open the URL at the end of the terminal printout (highlighted below)

<p align="center"><img src="https://user-images.githubusercontent.com/8583900/144759522-5306e61e-e30d-45e0-bb1a-ea8360e8c6da.png" width="70%" /></p>

To check the tasks run try opening the first task in the half day workshop folder and running the Jupyter Lab code (either click on the triangular run button or click on the first code cell and press shift and enter to execute that cell).
