import React from 'react';

const LoginForm = ({ config, setConfig, onConnect }) => {
  return (
    <div className="config-form">
      <input
        type="text"
        placeholder="GitHub Owner"
        value={config.owner}
        onChange={(e) => setConfig({ ...config, owner: e.target.value })}
      />
      <input
        type="password"
        placeholder="Personal Access Token"
        value={config.token}
        onChange={(e) => setConfig({ ...config, token: e.target.value })}
      />

      <div className="login-actions">
        <button onClick={onConnect}>Connect to GitHub</button>
        <span className="login-helper-text">First time user?</span>
        <a
          href="https://github.com/settings/tokens"
          target="_blank"
          rel="noopener noreferrer"
          className="create-token-link"
        >
          <span className="plus-icon">+</span> Create My Token
        </a>
      </div>
    </div>
  );
};

export default LoginForm;