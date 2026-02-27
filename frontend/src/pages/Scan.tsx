import { 
  IonContent, 
  IonHeader, 
  IonPage, 
  IonTitle, 
  IonToolbar, 
  IonCard, 
  IonCardContent, 
  useIonToast,
  useIonViewDidEnter,
  useIonViewWillLeave
} from '@ionic/react';
import { useState, useRef } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';

const Scan: React.FC = () => {
  const [presentToast] = useIonToast();
  const [scanResult, setScanResult] = useState<string | null>(null);
  
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);
  
  // This lock prevents us from spamming the backend if the camera can't pause
  const isProcessingRef = useRef(false);

  useIonViewDidEnter(() => {
    if (scannerRef.current) return;

    const scanner = new Html5QrcodeScanner(
      "reader",
      { fps: 10 }, // Scanning the whole image!
      false
    );
    
    scannerRef.current = scanner;
    scanner.render(onScanSuccess, onScanFailure);

    async function onScanSuccess(decodedText: string) {
      // If we are already processing a ticket, ignore any new scans
      if (!scannerRef.current || isProcessingRef.current) return;
      
      isProcessingRef.current = true; // Lock the gate!

      // Try to pause the video feed, but ignore the error if it's a static image upload
      try {
        scannerRef.current.pause(true);
      } catch (err) {
        console.warn("Could not pause (likely an image upload). Safe to ignore.");
      }

      try {
        // Extract the TUK-XXXXXX hash
        const match = decodedText.match(/TUK-[A-Z0-9]+/);
        if (!match) {
          presentToast({ message: 'Invalid QR Code Format', color: 'warning', duration: 2000 });
          resetScanner();
          return;
        }

        const ticketHash = match[0];

        // Ping your FastAPI backend
        const response = await fetch('http://127.0.0.1:8000/api/v1/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ticket_hash: ticketHash })
        });

        const data = await response.json();

        if (response.ok) {
          setScanResult(`✅ VALID: ${ticketHash}`);
          presentToast({ message: data.message, color: 'success', duration: 3000 });
        } else {
          setScanResult(`❌ REJECTED: ${ticketHash}`);
          presentToast({ message: data.detail, color: 'danger', duration: 3000 });
        }
      } catch (error) {
        presentToast({ message: 'Network error connecting to backend.', color: 'danger', duration: 2000 });
      }

      resetScanner();
    }

    function resetScanner() {
      // Wait 3 seconds, then unlock the gate and resume scanning
      setTimeout(() => {
        setScanResult(null);
        isProcessingRef.current = false;
        try {
          if (scannerRef.current) scannerRef.current.resume();
        } catch (err) {
          // Ignore error if it's an image upload
        }
      }, 3000);
    }

    function onScanFailure(error: any) {
      // Background noise, ignore
    }
  });

  useIonViewWillLeave(() => {
    if (scannerRef.current) {
      scannerRef.current.clear().catch(error => console.error("Failed to clear scanner", error));
      scannerRef.current = null;
    }
  });

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar color="dark">
          <IonTitle>Gatekeeper Scanner</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen className="ion-padding">
        <IonCard>
          <IonCardContent>
            <div id="reader" style={{ width: '100%', minHeight: '300px' }}></div>
            
            {scanResult && (
              <h2 style={{ textAlign: 'center', marginTop: '20px', fontWeight: 'bold' }}>
                {scanResult}
              </h2>
            )}
          </IonCardContent>
        </IonCard>
      </IonContent>
    </IonPage>
  );
};

export default Scan;