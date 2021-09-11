# Ansible Network role

Ansible role to configure network interfaces and routing on linux servers 

**Note:** this role currently only supports debian-based systems

## Functionality

This ansible role will configure:
* Configure the network interfaces
* Set-up static routing
* Add impermanent startup-interfaces (*sometimes needed for vpn tunnels*)

**Note:** Most of this functionality can be opted in or out using the main defaults file and variables!

## Usage

Just define the 'network' dictionary as needed:
```yaml
network:
```
or the compact way:
```yaml
network: {

}
```


### Example

**Config:**
```yaml
network:

```

**Result:**
```bash
ip a

ip route show

```
