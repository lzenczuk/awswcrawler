from aws.resource_manager import LocalFolderResourceCreationLogger, ResourceManager

rcl = LocalFolderResourceCreationLogger("build", "local_resources")
rm = ResourceManager(rcl)
rm.destroy()
