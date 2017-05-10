# vmssvmname

Python 3 script to convert Azure VM scale set VM hostnames into a VM ids. E.g.

```
> python vmssvmname.py --vmid 1146 --prefix myvmprefix
hostname = myvmprefix0000VU

> python vmssvmname.py --hostname myvmprefix0000VU
VM ID = 1146
```
