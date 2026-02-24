import {
  IonContent,
  IonHeader,
  IonPage,
  IonTitle,
  IonToolbar,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardSubtitle,
  IonCardContent,
  IonButton,
  IonInput,
  IonItem,
  useIonToast
} from '@ionic/react';
import { useState, useRef } from 'react';
import './Home.css';

const Home: React.FC = () => {
  const [phone, setPhone] = useState('254748228565');
  const [loading, setLoading] = useState(false);
  const [ticketHash, setTicketHash] = useState<string | null>(null);
  const [presentToast] = useIonToast();
  
  // We use a ref to hold the WebSocket connection
  const ws = useRef<WebSocket | null>(null);

  const triggerPayment = async () => {
    setLoading(true);
    try {
      // 1. Open the WebSocket Tunnel FIRST
      ws.current = new WebSocket(`ws://127.0.0.1:8000/api/v1/ws/${phone}`);
      
      ws.current.onmessage = (event) => {
        // The exact moment the backend sends the ticket hash!
        console.log("WebSocket received:", event.data);
        setTicketHash(event.data); 
        ws.current?.close(); // Close tunnel, we got what we needed
      };

      // 2. Trigger the actual M-Pesa Payment
      const response = await fetch('http://127.0.0.1:8000/api/v1/pay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone, amount: 1 })
      });

      const data = await response.json();

      if (data.ResponseCode === "0") {
        presentToast({
          message: 'Check your phone for the M-Pesa prompt!',
          duration: 4000,
          color: 'success'
        });
      } else {
        presentToast({ message: 'Failed to initiate.', duration: 3000, color: 'danger' });
        setLoading(false);
      }
    } catch (error) {
      presentToast({ message: 'Network error.', duration: 3000, color: 'danger' });
      setLoading(false);
    }
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar color="primary">
          <IonTitle>Tukio Events</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen className="ion-padding">
        
        <IonCard>
          {/* If we have a ticket, show the QR Code! Otherwise show the event image */}
          {ticketHash ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <h2>🎉 Payment Successful!</h2>
              <p>Here is your entry ticket:</p>
              <img 
                src={`http://127.0.0.1:8000/api/v1/ticket/${ticketHash}?phone=${phone}`} 
                alt="Ticket QR Code" 
                style={{ width: '250px', height: '250px', border: '2px solid #000', borderRadius: '10px' }}
              />
              <br/><br/>
              <b>Ticket ID: {ticketHash}</b>
            </div>
          ) : (
            <>
              <img alt="Tech Week" src="https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800" />
              <IonCardHeader>
                <IonCardSubtitle>Sept 14 - 16, 2026</IonCardSubtitle>
                <IonCardTitle>Nairobi Tech Week 2026</IonCardTitle>
              </IonCardHeader>

              <IonCardContent>
                <IonItem className="ion-margin-bottom">
                  <IonInput 
                    fill="outline"
                    label="M-Pesa Number" 
                    labelPlacement="floating" 
                    value={phone} 
                    onIonChange={e => setPhone(e.detail.value!)} 
                    type="tel"
                  />
                </IonItem>
                
                <IonButton expand="block" color="success" onClick={triggerPayment} disabled={loading}>
                  {loading ? 'Awaiting Payment...' : 'Pay KES 1 via M-Pesa'}
                </IonButton>
              </IonCardContent>
            </>
          )}
        </IonCard>

      </IonContent>
    </IonPage>
  );
};

export default Home;