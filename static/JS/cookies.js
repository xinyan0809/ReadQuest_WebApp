//  Cookies functionality
 
 (function () {
            function getCookie(name) {
                const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
                return match ? match[2] : null;
            }

            function setCookie(name, value, days) {
                const expires = new Date();
                expires.setDate(expires.getDate() + days);
                document.cookie = name + '=' + value + '; expires=' + expires.toUTCString() + '; path=/';
            }

            function dismissBanner() {
                document.getElementById('cookie-banner').style.display = 'none';
            }

            if (!getCookie('cookie_consent')) {
                document.getElementById('cookie-banner').style.display = 'block';
            }

            document.getElementById('cookie-accept-btn').addEventListener('click', function () {
                setCookie('cookie_consent', 'accepted', 365);
                dismissBanner();
            });

            document.getElementById('cookie-decline-btn').addEventListener('click', function () {
                setCookie('cookie_consent', 'declined', 30);
                dismissBanner();
            });
        })();