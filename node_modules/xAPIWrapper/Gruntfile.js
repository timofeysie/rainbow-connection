module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    'pkg': grunt.file.readJSON('package.json'),
    'bump': {
      options: {
        updateConfigs: ['pkg'],
        commitFiles: ['-a']
      }
    },
    'uglify': {
      options: {
        banner: '/*! <%= pkg.name %> v <%= pkg.version %> | Built on <%= grunt.template.today("yyyy-mm-dd HH:MM:sso") %> */\n'
      },
      'build': {
        files: {
          'dist/xapiwrapper.min.js': [
            'src/index.js'    // Everything is included from here
            // 'lib/cryptojs_v3.1.2.js',
            // 'src/verbs.js',
            // 'src/xapiwrapper.js',
            // 'src/xapistatement.js',
            // 'src/xapi-util.js',
            // 'src/xapi-launch.js'
          ]
        }
      }
    },
    'exec': {
      docs: './node_modules/doxstrap/bin/doxstrap.js --source "src/xapiwrapper.js:src/xapistatement.js" --title "xAPIWrapper <%= pkg.version %> Reference" --layout "bs-sidebar.html" --no-sort --output doc'
    },
    'webpack': {
      xapiwrapper: {
        entry: "./src/index.js",
        output: {
          path: "dist/",
          filename: "xapiwrapper.min.js"
        }
      }
    },
    watch: {
      files: ['src/*.js'],
      tasks: ['webpack'],
    }
  });

  // Load the plugins.
  grunt.loadNpmTasks('grunt-bump');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-exec');

  // Default task(s).
  grunt.registerTask('default', ['webpack']);//,'exec']);

  // Build only
  grunt.registerTask('build', ['webpack']);

  // Docs only
  grunt.registerTask('docs', ['exec']);

  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-webpack');


  // those with adl repo access can use this to publish a tag and release
  // $> grunt release:minor
  grunt.registerTask('release', 'Build the release of xapiwrapper', function(n) {
    var vertype = n;
    if (vertype == null) vertype = 'minor';
    grunt.task.run('bump-only:' + vertype, 'default', 'bump-commit');
  });

};
