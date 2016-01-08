var gulp = require('gulp');
var shell = require('gulp-shell');

gulp.task('default', shell.task([
  'virtualenv/bin/autopep8 ./mailchimpy --recursive --in-place',
  'virtualenv/bin/autopep8 ./tests --recursive --in-place'
]))