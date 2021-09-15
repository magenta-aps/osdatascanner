// Webpack uses this to work with directories
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const RemoveEmptyScriptsPlugin = require('webpack-remove-empty-scripts');
const CopyWebpackPlugin = require('copy-webpack-plugin')

// we want to put the files in both the admin and the report apps
const outputPaths = [
  '../projects/admin/adminapp/static',
  '../projects/report/reportapp/static'
]

// This is main configuration object.
// Here you write different options and tell Webpack what to do
module.exports = outputPaths.map(outputPath => {
  return {
    // Path to your entry point. From this file Webpack will begin his work
    entry: {
      js: {
        import: './js/main.js',
        filename: 'js/main.js'
      },
      scss: './scss/master.scss'
    },

    // Path of your result bundle.
    // Webpack will bundle all JavaScript into Django's static folder as per the
    // outputPaths const defined above
    output: {
      path: path.resolve(__dirname, outputPath)
    },

    // Default mode for Webpack is production.
    // We'll be overriding this property in dev and prod configs
    mode: 'production',

    module: {
      rules: [
        {
          test: /\.js$/,
          /* ... */
        },
        {
          // Apply rule for .sass, .scss or .css files
          test: /\.(sa|sc|c)ss$/,

          // Set loaders to transform files.
          // Loaders are applying from right to left(!)
          // The first loader will be applied after others
          use: [
            // split files into .css chunks instead of .js chunks
            MiniCssExtractPlugin.loader,
            {
              // This loader is necessary to prevent webpack from choking
              // on @import and url() inside (S)CSS files.
              loader: 'css-loader',
              options: {
                // don't resolve @import and url() as we will be statically copying over the resources they point to
                import: false,
                url: false
              }
            },
            {
              // First we transform SASS to standard CSS
              loader: 'sass-loader',
              options: {
                implementation: require('sass'),
                sourceMap: true
              }
            }
          ]
        },
        {
          // Now we apply rule for images
          test: /\.(png|jpe?g|gif|svg)$/,
          use: [
            {
              // Using file-loader for these files
              loader: 'file-loader',

              // In options we can set different things like format
              // and directory to save
              options: {
                outputPath: 'images',
                name: '[name].[ext]'
              }
            }
          ]
        },
        {
          // Apply rule for fonts files
          test: /\.(woff|woff2|ttf|otf|eot)$/,
          use: [
            {
              // Using file-loader too
              loader: 'file-loader',
              options: {
                outputPath: 'fonts',
                name: '[name].[ext]'
              }
            }
          ]
        },
      ]
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: 'css/master.css'
      }),
      // webpack will create a JS file for an entry file, which is useless if the
      // entry file is a SCSS file or similar.
      new RemoveEmptyScriptsPlugin(),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: '3rdparty',
            to: '3rdparty'
          },
          {
            from: 'admin',
            to: 'admin'
          },
          {
            from: 'css',
            to: 'css'
          },
          {
            from: 'favicons',
            to: 'favicons'
          },
          {
            from: 'fonts',
            to: 'fonts'
          },
          {
            from: 'js',
            to: 'js'
          },
          {
            from: 'recurrence',
            to: 'recurrence'
          },
          {
            from: 'svg',
            to: 'svg'
          }
        ]
      })
    ]
  }
})
