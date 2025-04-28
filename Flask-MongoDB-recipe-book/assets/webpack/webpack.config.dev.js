const Path = require('path');
const Webpack = require('webpack');
const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const BrowserSyncPlugin = require('browser-sync-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = merge(common, {
    mode: 'development',
    devtool: 'cheap-eval-source-map',
    output: {
        chunkFilename: 'js/[name].chunk.js'
    },
    devServer: {
        inline: true,
    },
    plugins: [
        new Webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('development')
        }),
        new MiniCssExtractPlugin({
            filename: 'css/app.css'
        }),
        new BrowserSyncPlugin(
            // BrowserSync options
            // https://www.browsersync.io/docs/options
            {
                // browse to http://localhost:3000/ during development
                host: 'localhost',
                port: 3000,
                proxy: 'http://127.0.0.1:5000/',
                reloadDelay: 500, // help with browser cache
                open: false,
                files: [
                    "*.py",
                    "**/*.py",
                    "templates/**/*.html"
                ]
            },
            // plugin options
            {
                injectCss: true,
                reload: true,
            }
        )
    ],
    module: {
        rules: [
            {
                test: /\.(js)$/,
                include: Path.resolve(__dirname, '../../assets'),
                enforce: 'pre',
                loader: 'eslint-loader',
                options: {
                    emitWarning: true,
                }
            },
            {
                test: /\.(js)$/,
                include: Path.resolve(__dirname, '../../assets'),
                loader: 'babel-loader'
            },
            {
                test: /\.s?css$/i,
                /*include: Path.resolve(__dirname, '../../assets'),
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader'
                ]*/
                // include: Path.resolve(__dirname, '../../assets'),
                use: ['style-loader', 'css-loader?sourceMap=true', 'sass-loader']
            },
            {
                test: /\.(ico|jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2)(\?.*)?$/,
                include: /node_modules/,
                use: {
                    loader: 'file-loader',
                    options: {
                        publicPath: 'http://localhost:3000/static/vendor/',
                        outputPath: 'vendor/',
                        name: '[name].[ext]'
                    }
                }
            }
        ]
    },
});
