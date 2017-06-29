from django_assets import Bundle, register

js = Bundle('jquery/dist/jquery.js',
            'bootstrap-sass/assets/javascripts/bootstrap.js',
            output='app.js')
register('script', js)

css = Bundle('style/id.scss',
             filters='libsass',
             depends=['**/*.scss'],
             output='style.css')
register('style', css)
