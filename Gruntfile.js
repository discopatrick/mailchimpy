module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({

    flake8: {
      options: {
        // Task-specific options go here.
        ignore: []
      },
      src: [
        // Files to lint go here.
        'mailchimpy/**/*.py',
      ],
      tests: [
        'tests/**/*.py',
      ]
    },

  });

  // Load the plugin that provide the tasks.
  grunt.loadNpmTasks('grunt-flake8');

  // Default task(s).
  grunt.registerTask('default', ['flake8']);

};