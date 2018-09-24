import $ from 'jquery';
import 'babel-polyfill';
// Uncomment the lines below if using react
// import * as React from 'react';
// import * as ReactDOM from 'react-dom';
// import TestReact from './components/test-react';

import MobileMenu from './components/mobile-menu';
import MobileSubMenu from './components/mobile-sub-menu';

// Cookie notification
import './components/cookie-message';

// Open the mobile menu callback
function openMobileMenu() {
    document.querySelector('body').classList.add('no-scroll');
    document.querySelector('.js-mobile-menu').classList.add('is-visible');
}

// Close the mobile menu callback.
function closeMobileMenu() {
    document.querySelector('body').classList.remove('no-scroll');
    document.querySelector('.js-mobile-menu').classList.remove('is-visible');
}

$(function () {
    $(MobileMenu.selector()).each((index, el) => {
        new MobileMenu($(el), openMobileMenu, closeMobileMenu);
    });

    $(MobileSubMenu.selector()).each((index, el) => {
        new MobileSubMenu($(el));
    });

    // Toggle subnav visibility
    $('.js-subnav-back').on('click', function(){
        this.parentNode.classList.remove('is-visible');
    });
});


// Test react
// for (let element of document.querySelectorAll('.js-test-react')) {
//     ReactDOM.render(
//         <TestReact
//             greeting="boo!"
//         />,
//         element
//     );
// }
