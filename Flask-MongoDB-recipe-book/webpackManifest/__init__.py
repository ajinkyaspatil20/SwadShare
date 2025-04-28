import json
import os


class WebpackManifest:
    JsonExist = False
    manifest = {}

    def __init__(self, app, params: dict):
        try:
            self.staticFolder = params['static_folder']
            self.manifestPath = params['manifest_path']
            self.app = app
            self.JsonExist = self._file_exists(self.manifestPath)
            self.init_app()
        except IOError:
            raise RuntimeError(
                "Incorrect parameters passed to WebpackManifest"
                "it must point to a valid json file.")

    def init_app(self):
        self._set_asset_paths()
        self.app.add_template_global(self.manifest_js)
        self.app.add_template_global(self.manifest_css)
        # app.add_template_global(self.asset_url_for)

    def _set_asset_paths(self):
        if self.JsonExist:
            with self.app.open_resource(self.manifestPath, 'r') as stats_json:
                self.manifest = json.load(stats_json)

    def manifest_js(self, args):
        if self.JsonExist and args in self.manifest:
            asset_path = '{}/{}'.format(self.staticFolder, self.manifest[args])
            return '<script src="{0}"></script>'.format(asset_path)
            # return False
        else:
            return ''

    def manifest_css(self, args):
        if self.JsonExist and args in self.manifest:
            asset_path = '{}/{}'.format(self.staticFolder, self.manifest[args])
            return '<link rel="stylesheet" href="{0}">'.format(asset_path)
        else:
            return ''

    @staticmethod
    def _file_exists(path):
        return os.path.isfile(path)
