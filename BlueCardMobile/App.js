import React from 'react';
import { View } from 'react-native';
import { WebView } from 'react-native-webview';  // Import WebView to load the website

export default function App() {
  return (
    <View style={{ flex: 1 }}>
      {/* WebView will load your Dash app */}
      <WebView
        source={{ uri: 'https://bluecard.onrender.com' }}  // Your Dash app URL
        style={{ flex: 1 }}
      />
    </View>
  );
}
