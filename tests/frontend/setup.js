/**
 * Jest setup file for WebRTC browser API mocks
 */

// Mock RTCPeerConnection
class MockRTCPeerConnection {
  constructor(config) {
    this.config = config;
    this.iceConnectionState = 'new';
    this.iceGatheringState = 'new';
    this.localDescription = null;
    this.remoteDescription = null;
    this.ontrack = null;
    this.oniceconnectionstatechange = null;
    this.transceivers = [];
  }

  addTransceiver(kind, init) {
    this.transceivers.push({ kind, init });
  }

  async createOffer() {
    return { type: 'offer', sdp: 'fake-offer-sdp' };
  }

  async setLocalDescription(desc) {
    this.localDescription = desc;
    this.iceGatheringState = 'complete';
    return Promise.resolve();
  }

  async setRemoteDescription(desc) {
    this.remoteDescription = desc;
    this.iceConnectionState = 'connected';
    return Promise.resolve();
  }

  close() {
    this.iceConnectionState = 'closed';
  }

  addEventListener(event, handler) {
    if (event === 'icegatheringstatechange') {
      this._iceGatheringHandler = handler;
    }
  }

  removeEventListener(event, handler) {
    if (event === 'icegatheringstatechange') {
      this._iceGatheringHandler = null;
    }
  }
}

global.RTCPeerConnection = MockRTCPeerConnection;

// Mock MediaStream
class MockMediaStream {
  constructor() {
    this.tracks = [];
  }

  getTracks() {
    return this.tracks;
  }

  addTrack(track) {
    this.tracks.push(track);
  }
}

global.MediaStream = MockMediaStream;

// Mock MediaStreamTrack
class MockMediaStreamTrack {
  constructor(kind = 'video') {
    this.kind = kind;
    this.enabled = true;
  }

  stop() {
    this.enabled = false;
  }
}

global.MediaStreamTrack = MockMediaStreamTrack;

// Mock Hls.js
global.Hls = class Hls {
  static isSupported() {
    return true;
  }

  constructor(config) {
    this.config = config;
    this.media = null;
    this.eventHandlers = {};
  }

  loadSource(url) {
    this.url = url;
  }

  attachMedia(video) {
    this.media = video;
  }

  on(event, handler) {
    this.eventHandlers[event] = handler;
  }

  static get Events() {
    return {
      MANIFEST_PARSED: 'hlsManifestParsed',
      ERROR: 'hlsError'
    };
  }
};

// Mock fetch
global.fetch = jest.fn((url) => {
  if (url.includes('/api/webrtc')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      text: () => Promise.resolve('v=0\r\no=- 123 456 IN IP4 127.0.0.1\r\ns=WebRTC\r\n')
    });
  }
  return Promise.reject(new Error('Unknown endpoint'));
});

// Suppress console output during tests
global.console = {
  ...console,
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};
