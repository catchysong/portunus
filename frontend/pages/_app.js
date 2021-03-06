import { useEffect } from 'react';
import { observer } from 'mobx-react';
import PropTypes from 'prop-types';
import Head from 'next/head';
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/core/styles';
import theme from '@wui/theme';
import 'mobx-react-lite/batchingForReactDom';

import * as Sentry from '@sentry/react';

import GlobalContextProvider from '@@/global-context';
import { setupCsrf } from '@@/utils/API';
import Nav from '@@/components/Nav';
import ChatWidget from '@@/components/ChatWidget';
import ProtectedPage from '@@/components/ProtectedPage';
import { ZENDESK_CHAT_KEY } from '@@/utils/constants/chat';
import { googleAnalyticsEffect } from '@@/utils/google-analytics';

import env from 'utils/env';

import '@@/global.css';

if (typeof window !== 'undefined') {
  Promise.all([env.sentry_dsn, env.sentry_environment])
    .then(([dsn, environment]) => {
      Sentry.init({ dsn, environment });
    })
    .catch(() => null);
}

const App = ({ Component, pageProps }) => {
  useEffect(() => {
    // Remove the server-side injected CSS.
    const jssStyles = document.querySelector('#jss-server-side');
    if (jssStyles) {
      jssStyles.parentElement.removeChild(jssStyles);
    }
  });

  useEffect(() => {
    // Ensure the CSRF cookie is set.
    setupCsrf();
  }, []);

  useEffect(googleAnalyticsEffect, []);

  const ProtectComponent = Component.public ? React.Fragment : ProtectedPage;

  return (
    <GlobalContextProvider>
      <ThemeProvider theme={theme}>
        <Head>
          <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0"
          />

          <link rel="stylesheet" href="/averta.css" />
          <ChatWidget apiKey={ZENDESK_CHAT_KEY} />
        </Head>

        <CssBaseline />
        <ProtectComponent>
          <Nav />
          <Component {...pageProps} />
        </ProtectComponent>
      </ThemeProvider>
    </GlobalContextProvider>
  );
};

App.propTypes = {
  Component: PropTypes.elementType.isRequired,
  pageProps: PropTypes.object,
};

App.defaultProps = {
  pageProps: {},
};

export default observer(App);
