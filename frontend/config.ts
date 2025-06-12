interface Config {
  apiBaseUrl: string;
}

const config: Config = {
  apiBaseUrl: window.location.hostname === 'localhost' 
    ? "http://localhost:8000" 
    : "http://164.92.184.138:8000"
};

export default config;