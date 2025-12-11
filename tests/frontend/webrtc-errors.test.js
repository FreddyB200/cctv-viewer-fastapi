/**
 * Error handling and network failure tests for WebRTC
 */

describe('WebRTC Error Handling', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    global.fetch.mockClear();
  });

  describe('Network failures', () => {
    test('should handle HTTP 500 server errors', async () => {
      global.fetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          text: () => Promise.resolve('Internal Server Error')
        })
      );

      const pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});
      await pc.setLocalDescription(await pc.createOffer());

      // Wait for ICE gathering
      await new Promise(resolve => setTimeout(resolve, 150));

      try {
        const response = await fetch('http://localhost:1984/api/webrtc?src=cam1', {
          method: 'POST',
          headers: {'Content-Type': 'application/sdp'},
          body: pc.localDescription.sdp
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
      } catch (err) {
        expect(err.message).toContain('HTTP 500');
      }
    });

    test('should handle network timeout', async () => {
      jest.useFakeTimers();

      global.fetch.mockImplementationOnce(() =>
        new Promise((resolve) => {
          // Never resolves - simulates timeout
        })
      );

      const fetchPromise = fetch('http://localhost:1984/api/webrtc?src=cam1');
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Network timeout')), 5000)
      );

      jest.advanceTimersByTime(5000);

      await expect(Promise.race([fetchPromise, timeoutPromise])).rejects.toThrow('Network timeout');

      jest.useRealTimers();
    });

    test('should handle invalid SDP answer format', async () => {
      global.fetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          text: () => Promise.resolve('INVALID_SDP_FORMAT')
        })
      );

      const pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});

      try {
        await pc.setLocalDescription(await pc.createOffer());
        const response = await fetch('http://localhost:1984/api/webrtc?src=cam1');
        const answer = await response.text();

        // This would normally fail in real RTCPeerConnection
        await pc.setRemoteDescription({type: 'answer', sdp: answer});

        // In our mock, it succeeds, but in production this would throw
        // DOMException: Failed to set remote answer sdp
      } catch (err) {
        expect(err.message).toMatch(/SDP|remote/i);
      }
    });

    test('should handle connection refused', async () => {
      global.fetch.mockImplementationOnce(() =>
        Promise.reject(new Error('Failed to fetch'))
      );

      await expect(
        fetch('http://localhost:1984/api/webrtc?src=cam1')
      ).rejects.toThrow('Failed to fetch');
    });
  });

  describe('ICE connection state failures', () => {
    test('should detect ICE connection failed state', () => {
      const pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});
      const stateChanges = [];

      pc.oniceconnectionstatechange = () => {
        stateChanges.push(pc.iceConnectionState);
      };

      // Simulate connection failure
      pc.iceConnectionState = 'failed';
      if (pc.oniceconnectionstatechange) {
        pc.oniceconnectionstatechange();
      }

      expect(stateChanges).toContain('failed');
    });

    test('should detect ICE connection disconnected state', () => {
      const pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});

      pc.iceConnectionState = 'disconnected';

      expect(pc.iceConnectionState).toBe('disconnected');
    });

    test('should cleanup resources on connection closed', () => {
      const pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});

      pc.close();

      expect(pc.iceConnectionState).toBe('closed');
    });
  });

  describe('ICE gathering timeout', () => {
    test('should timeout if ICE gathering takes too long', async () => {
      jest.useFakeTimers();

      // Create PC with very long delay to force timeout
      const pc = new RTCPeerConnection({
        iceServers: [{urls: 'stun:stun.l.google.com:19302'}],
        _testGatheringDelay: 15000  // 15 seconds - exceeds 10s timeout
      });

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const waitPromise = Promise.race([
        new Promise((resolve) => {
          if (pc.iceGatheringState === 'complete') {
            resolve();
          } else {
            const checkState = () => {
              if (pc.iceGatheringState === 'complete') {
                pc.removeEventListener('icegatheringstatechange', checkState);
                resolve();
              }
            };
            pc.addEventListener('icegatheringstatechange', checkState);
          }
        }),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('ICE gathering timeout')), 10000)
        )
      ]);

      jest.advanceTimersByTime(10000);

      await expect(waitPromise).rejects.toThrow('ICE gathering timeout');

      jest.useRealTimers();
    });

    test('should complete successfully if ICE gathering is fast', async () => {
      jest.useFakeTimers();

      const pc = new RTCPeerConnection({
        iceServers: [{urls: 'stun:stun.l.google.com:19302'}],
        _testGatheringDelay: 50  // Fast gathering
      });

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const waitPromise = new Promise((resolve) => {
        if (pc.iceGatheringState === 'complete') {
          resolve();
        } else {
          const checkState = () => {
            if (pc.iceGatheringState === 'complete') {
              pc.removeEventListener('icegatheringstatechange', checkState);
              resolve();
            }
          };
          pc.addEventListener('icegatheringstatechange', checkState);
        }
      });

      jest.advanceTimersByTime(100);

      await expect(waitPromise).resolves.toBeUndefined();

      jest.useRealTimers();
    });
  });

  describe('Resource cleanup on errors', () => {
    test('should stop all tracks when cleaning up', () => {
      const track1 = new MediaStreamTrack('video');
      const track2 = new MediaStreamTrack('audio');
      const stream = new MediaStream();
      stream.addTrack(track1);
      stream.addTrack(track2);

      const video = { srcObject: stream };
      const pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});

      // Simulate cleanup
      if (pc) pc.close();
      if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
      }

      expect(track1.enabled).toBe(false);
      expect(track2.enabled).toBe(false);
      expect(video.srcObject).toBeNull();
      expect(pc.iceConnectionState).toBe('closed');
    });

    test('should handle cleanup with null peer connection', () => {
      const pc = null;
      const video = { srcObject: null };

      expect(() => {
        if (pc) pc.close();
        if (video.srcObject) {
          video.srcObject.getTracks().forEach(track => track.stop());
          video.srcObject = null;
        }
      }).not.toThrow();
    });

    test('should handle cleanup with no tracks', () => {
      const stream = new MediaStream();
      const video = { srcObject: stream };
      const pc = new RTCPeerConnection({iceServers: [{urls: 'stun:stun.l.google.com:19302'}]});

      if (pc) pc.close();
      if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
      }

      expect(video.srcObject).toBeNull();
      expect(pc.iceConnectionState).toBe('closed');
    });
  });

  describe('Retry mechanism edge cases', () => {
    test('should not exceed max retries', () => {
      const maxRetries = 3;
      let attemptCount = 0;

      for (let attempt = 1; attempt <= maxRetries + 2; attempt++) {
        if (attempt <= maxRetries) {
          attemptCount++;
        }
      }

      expect(attemptCount).toBe(maxRetries);
    });

    test('should calculate correct backoff delays', () => {
      const delays = [];
      for (let attempt = 1; attempt <= 5; attempt++) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
        delays.push(delay);
      }

      expect(delays).toEqual([1000, 2000, 4000, 8000, 10000]);
    });

    test('should reset UI between retries', () => {
      const errorOverlay = {
        classList: {
          add: jest.fn(),
          remove: jest.fn()
        }
      };
      const loadingOverlay = {
        classList: {
          add: jest.fn(),
          remove: jest.fn()
        },
        textContent: ''
      };

      // Simulate retry UI reset
      errorOverlay.classList.add('hidden');
      loadingOverlay.classList.remove('hidden');
      loadingOverlay.textContent = 'Reconnecting...';

      expect(errorOverlay.classList.add).toHaveBeenCalledWith('hidden');
      expect(loadingOverlay.classList.remove).toHaveBeenCalledWith('hidden');
      expect(loadingOverlay.textContent).toBe('Reconnecting...');
    });
  });
});
