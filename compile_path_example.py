from pyVim.connect import SmartConnect, Disconnect
import ssl
import atexit
from pyVmomi import vim

context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.verify_mode = ssl.CERT_NONE

si = SmartConnect(host='0.0.0.0', user='user', pwd='pass', port=443, sslContext=context)
atexit.register(Disconnect, si)
content = si.RetrieveContent()


def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break

    container.Destroy()
    return obj


def compile_folder_path_for_object(vobj):
    """ make a /vm/foo/bar/baz like folder path for an object """

    paths = []
    if isinstance(vobj, vim.Folder):
        paths.append(vobj.name)

    broke = False

    thisobj = vobj
    while True:
        try:
            thisobj = thisobj.parent
            if thisobj is None:
                broke = True
                break
        except (IndexError, AttributeError) as err:
            broke = True
            break
        if isinstance(thisobj, vim.Folder):
            paths.append(thisobj.name)
        else:
            """ break as soon as we hit something that is not a folder """
            break
    if broke:
        """ we reached the top. Remove the 'datacenters' folder from the list """
        paths.pop()
    paths.reverse()
    return '/' + '/'.join(paths)

datacenter = get_obj(content, [vim.Datacenter], 'DC0')
print(compile_folder_path_for_object(datacenter))

vm = get_obj(content, [vim.VirtualMachine], 'DC0_H0_VM0')
print(compile_folder_path_for_object(vm))

ds = get_obj(content, [vim.Datastore], 'LocalDS_0')
print(compile_folder_path_for_object(ds))

dvs = get_obj(content, [vim.DistributedVirtualSwitch], 'DVS0')
print(compile_folder_path_for_object(dvs))

rp = get_obj(content, [vim.ResourcePool], 'DC0_C0_RP1')
print(compile_folder_path_for_object(rp))
