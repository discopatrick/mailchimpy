var gulp = require('gulp');
var shell = require('gulp-shell');

gulp.task('lint-src', shell.task([
  'virtualenv/bin/autopep8 ./mailchimpy --recursive --in-place',
]));

gulp.task('lint-tests', shell.task([
  'virtualenv/bin/autopep8 ./tests --recursive --in-place'
]));

gulp.task('default', ['lint-src', 'lint-tests']);