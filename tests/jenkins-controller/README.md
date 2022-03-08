# jenkins config

* [Configuration as Code Plugin](https://github.com/jenkinsci/configuration-as-code-plugin) is leveraged for configuration of Jenkins at runtime
* config from [common](config/common) is applied to all jenkins instances
* config from other directories, such as [local-test](config/local-test), is applied _only_ if the directory name matches the `PLATFORM_ID` environment variable.

## development

### reference

#### dump list of currently installed plugins

visit `http://jenkins/script`, e.g. http://localhost:8080/script

```
List<String> jenkinsPlugins = new ArrayList<String>(Jenkins.instance.pluginManager.plugins);
jenkinsPlugins.sort { it.shortName }.each{
  plugin ->
    println ("${plugin.getShortName()}:${plugin.getVersion()}")
}
return
```
