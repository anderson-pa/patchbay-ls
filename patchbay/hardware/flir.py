import warnings
from collections import namedtuple

import PySpin


class FlirAPI:
    def __init__(self):
        self.system = PySpin.System.GetInstance()

    def __del__(self):
        self.system.ReleaseInstance()

    def _get_items(self, item_type, interface_id=None):
        """Get an iterator of PySpin.system items (interfaces or cameras).

        :param item_type: 'interfaces' or 'cameras'
        :param interface_id: if provided, search interface instead of system
        :return: iterator of item_types
        """
        if interface_id:
            source = self.get_interface(interface_id)
        else:
            source = self.system

        items = getattr(source, f'Get{item_type.capitalize()}')()
        x = None
        try:
            for x in items:
                yield x
        finally:
            del x
            items.Clear()

    def version(self):
        """Return the PySpin library version."""
        version = self.system.GetLibraryVersion()
        return version.major, version.minor, version.type, version.build

    def list_interfaces(self):
        """Get a list of IDs and names for available interfaces.

        :return: list of interface details
        """
        interface_list = []
        for interface in self._get_items('interfaces'):
            nodemap = FlirNodeMap(interface.GetTLNodeMap())
            interface_id = nodemap.get('InterfaceID')
            name = nodemap.get('InterfaceDisplayName')

            interface_list.append((interface_id, name))
        return interface_list

    def get_interface(self, interface_id):
        """Get an interface instance for the given ID.

        Raises ValueError if a suitable interface is not found. All instances
        must be removed from memory before the `system` instance can be
        released.

        :param interface_id: ID of the interface to return
        :return: `PySpin.InterfacePtr` instance
        """
        for interface in self._get_items('interfaces'):
            nodemap = FlirNodeMap(interface.GetTLNodeMap())
            if nodemap.get('InterfaceID') == interface_id:
                return interface
        raise ValueError(f'Interface not found with ID: {interface_id}')

    def list_cameras(self, interface_id=None):
        """Get a list of IDs and names for available cameras.

        :param interface_id: ID of the interface to search, or 'system' if None
        :return: list of camera details
        """
        camera_list = []
        for camera in self._get_items('cameras', interface_id=interface_id):
            nodemap = FlirNodeMap(camera.GetTLDeviceNodeMap())
            device_id = nodemap.get('DeviceID')
            vendor_name = nodemap.get('DeviceVendorName')
            model_name = nodemap.get('DeviceModelName')

            camera_list.append((device_id, f'{vendor_name}: {model_name}'))
        return camera_list

    def get_camera(self, camera_id, interface_id=None):
        """Get a camera instance for the given ID.

        By default this searches the system camera list but can be restricted
        to a particular interface by passing in `interface_id`. Raises a
        ValueError if a suitable camera is not found. All instances must be
        removed from memory before the `system` instance can be released.

        :param camera_id: ID of the camera to return
        :param interface_id: ID of the interface to search, or `system` if None
        :return: `PySpin.CameraPtr` instance
        """
        for camera in self._get_items('cameras', interface_id=interface_id):
            nodemap = FlirNodeMap(camera.GetTLDeviceNodeMap())
            if nodemap.get('DeviceID') == camera_id:
                return FlirCamera(camera)
        raise ValueError(f'Camera not found with ID: {camera_id}')


NodeInfo = namedtuple('NodeInfo', 'name, type')
node_types = {getattr(PySpin, x): x[5:] for x in vars(PySpin)
              if x.startswith('intf')}


class FlirNodeMap:
    def __init__(self, nodemap):
        self._nodemap = nodemap

    @staticmethod
    def _to_specific_node_type(node):
        """Convert a Ptr to a node to a more specific type."""
        node_func = f'C{node_types[node.GetPrincipalInterfaceType()]}Ptr'
        return getattr(PySpin, node_func)(node)

    def get_node(self, node_name):
        """Retrieve a node from nodemap.

        :param node_name: the name of the node to return
        :return:
        """
        node = self._nodemap.GetNode(node_name)
        return self._to_specific_node_type(node)

    @staticmethod
    def _get_node_info(node):
        return NodeInfo(node.GetName(),
                        node_types[node.GetPrincipalInterfaceType()])

    def _get_features(self, node):
        return [self._get_node_info(x) for x in node.GetFeatures()]

    def _get_features_by_name(self, node_name):
        return self._get_features(self.get_node(node_name))

    def get_node_options(self, node_name):
        node = self.get_node(node_name)
        try:
            options = [x.GetDisplayName() for x in node.GetEntries()]
        except AttributeError:
            options = []
        return options

    def get_feature_tree(self, node_name='Root'):
        tree = {feature.name: feature.type
                for feature in self._get_features_by_name(node_name)}
        for key in tree:
            if tree[key] == 'Category':
                tree[key] = self.get_feature_tree(key)
        return tree

    def get_features_flat(self, node_name='Root'):
        features = []

        for feature in self._get_features_by_name(node_name):
            if feature.type == 'Category':
                features.extend(self.get_features_flat(feature.name))
            else:
                features.append(feature)
                # node = self.get_node(feature.name)
                # features.insert(i + 1, *self._get_features(node))
        return features

    def get(self, node_name):
        node = self.get_node(node_name)
        if PySpin.IsAvailable(node) and PySpin.IsReadable(node):
            try:
                return node.GetValue()
            except AttributeError:
                # Enumerations use this method instead of GetValue()
                return node.ToString()
        else:
            warnings.warn(f'Node {node_name} is not available or readable')
            return None

    def set(self, node_name, new_value):
        node = self.get_node(node_name)
        if PySpin.IsAvailable(node) and PySpin.IsWritable(node):
            try:
                ok = node.SetValue(new_value)
                return ok
            except AttributeError:
                pass

            try:
                # Enumerations use this method instead of SetValue()
                ok = node.SetIntValue(node.GetEntryByName(new_value).GetValue())
                return ok
            except AttributeError:
                warnings.warn(f'Not a valid value for node {node_name}')
        else:
            warnings.warn(f'Node {node_name} is not available or writeable')
        return False

    def execute(self, node_name, *args):
        node = self.get_node(node_name)
        if PySpin.IsAvailable(node):
            node.Execute(*args)
        else:
            warnings.warn(f'Node {node_name} is not available.')


class FlirCamera:
    def __init__(self, camera_ptr):
        self._camera_ptr = camera_ptr
        self._camera_ptr.Init()

        self._nodemap = FlirNodeMap(self._camera_ptr.GetNodeMap())
        self._nodemap_tld = FlirNodeMap(self._camera_ptr.GetTLDeviceNodeMap())
        self._nodemap_tls = FlirNodeMap(self._camera_ptr.GetTLStreamNodeMap())

    def __del__(self):
        if self._camera_ptr.IsStreaming():
            self._camera_ptr.EndAcquisition()
        self._camera_ptr.DeInit()
        del self._camera_ptr

    def start(self):
        if not self._camera_ptr.IsStreaming():
            self._camera_ptr.BeginAcquisition()

    def update(self):
        pass

    def read(self, timeout=None):
        if timeout is None:
            timeout = PySpin.EVENT_TIMEOUT_INFINITE
        try:
            image = self._camera_ptr.GetNextImage(timeout)
        except PySpin.SpinnakerException as e:
            raise TimeoutError('Image acquisition timed out.')

        image_out = None
        if image.IsIncomplete():
            print('Image incomplete with '
                  'status %d ...' % image.GetImageStatus())
        else:
            width = image.GetWidth()
            height = image.GetHeight()

            image_out = image.Convert(PySpin.PixelFormat_Mono8,
                                      PySpin.HQ_LINEAR)
            image_out = image_out.GetData().reshape((height, width))

            image.Release()
        return image_out

    def stop(self):
        try:
            self._camera_ptr.EndAcquisition()
        except PySpin.SpinnakerException:
            pass
