import ReactGA from 'react-ga';
import Router from 'next/router';
import GOOGLE_ANALYTICS_ID from 'utils/constants/google';

export const initializeGoogleAnalytics = () => {
  ReactGA.initialize(GOOGLE_ANALYTICS_ID);
};

export const googleAnalyticsPageView = url => {
  ReactGA.set({ page: url || window.location.pathname });
  ReactGA.pageview(url || window.location.pathname);
};

export const googleAnalyticsEffect = () => {
  initializeGoogleAnalytics();
  Router.events.on('routeChangeComplete', googleAnalyticsPageView);
  return () => {
    Router.events.off('routeChangeComplete', googleAnalyticsPageView);
  };
};
