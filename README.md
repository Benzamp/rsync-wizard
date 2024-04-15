# Rsync Wizard

![Rsync Wizard](https://github.com/Benzamp/rsync-wizard/assets/39504919/4066eaf0-9aea-4bde-b259-0c0e2142db56)

**Created by Ben Harrison**

## Overview

Rsync Wizard is a graphical user interface (GUI) tool designed to simplify the generation of rsync commands using the OpenShift command-line tool (`oc`). It allows users to easily log in to an OKD cluster, select projects and pods, specify source and destination paths, and execute rsync commands.

## Usage

1. **Login Command**: Paste the copied OKD login command and press "Login" to populate the Projects dropdown.
2. **Projects Dropdown**: Choose an OKD project. Selecting one will populate the Pods dropdown with the pods of the project.
3. **Pods Dropdown**: Choose a pod, and the Source Path will update with that pod's plugin folder.
4. **Source Path**: Specify the folder you want to rsync from.
5. **Destination Path**: Specify the folder you'd like to rsync to. You can either browse or type in the path.
6. **No Perms Checkbox**: Check this box to add the `--no-perms=true` flag to the end of the command.

## Note

There may be issues if rsync isn't installed or configured in the path.

