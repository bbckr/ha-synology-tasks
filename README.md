# Synology Tasks HACS Integration

This integration extends the official [Synology DSM integration](https://www.home-assistant.io/integrations/synology_dsm/) in Home Assistant to provide control over your Synology NAS scheduled tasks. It automatically discovers all scheduled tasks configured on your NAS and creates:

- A **button entity** for each task to manually trigger it
- A **sensor entity** for each task to show its current status

All entities are grouped under the same device as your existing Synology DSM integration, keeping everything organized.

## Security Notice

**Important:** This integration reuses the credentials from your existing Synology DSM integration to authenticate with your NAS against the DSM API. It only accesses the specific NAS device that you configure with this integration. If you are not comfortable with this credential sharing approach, please do not use this integration.

## Prerequisites

- A Synology NAS device properly configured and accessible
- The official [Synology DSM integration](https://www.home-assistant.io/integrations/synology_dsm/) already set up and working in Home Assistant
- Scheduled tasks configured in your Synology DSM Task Scheduler

## Limitations & Disclaimers

This is a very early alpha integration that I've developed for my own use. While it works in my single NAS setup, it hasn't been extensively tested.

Feel free to open issues if you encounter problems or have suggestions for improving the quality of the integration.

## Local Development

### Requirements

- Docker or Podman
- pipx
- Poetry
    ```
    pipx install poetry
    ```

## Debugging against Home Assistant Locally

1. Run `docker-compose up`
1. Open http://0.0.0.0:8123 in your browser
1. Setup the first user
1. Install the **Remote Python Debugger** by adding the following to your configuration.yaml:
    ```
    debugpy:
    start: true
    wait: false
    ```
1. Run the **Home Assistant: Attach Remote** launch.json configuration
1. Set your breakpoints
1. Profit
