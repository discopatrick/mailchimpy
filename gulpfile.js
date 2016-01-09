var gulp = require('gulp');
var shell = require('gulp-shell');

gulp.task('lint', shell.task([
  'virtualenv/bin/autopep8 ./mailchimpy --recursive --in-place',
  'virtualenv/bin/autopep8 ./tests --recursive --in-place'
]));

gulp.task('test', shell.task(
  ['virtualenv/bin/python -m unittest'],
  { ignoreErrors: true }
));

gulp.task('watch', function() {
  gulp.watch('mailchimpy/**/*.py', ['test']);
  gulp.watch('tests/**/*.py', ['test']);
});

gulp.task('default', ['watch']);