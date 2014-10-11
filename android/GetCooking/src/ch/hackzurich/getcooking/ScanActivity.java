package ch.hackzurich.getcooking;

import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.Window;
import android.view.WindowManager;
import android.widget.Toast;

import com.mirasense.scanditsdk.ScanditSDKAutoAdjustingBarcodePicker;
import com.mirasense.scanditsdk.interfaces.ScanditSDK;
import com.mirasense.scanditsdk.interfaces.ScanditSDKListener;

public class ScanActivity extends ActionBarActivity implements ScanditSDKListener {
	
	// The main object for recognizing a displaying barcodes.
    private ScanditSDK mBarcodePicker;
    
    // Enter your Scandit SDK App key here.
    // Your Scandit SDK App key is available via your Scandit SDK web account.
    public static final String sScanditSdkAppKey = "oV/Wzk5DEeSQUeGdK5vfsPz8+7BrOnfnciXpNvsI0qM";
    

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		initializeAndStartBarcodeScanning();
		//setContentView(R.layout.activity_scan);
		
		// Initialize and start the bar code recognition.
        
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.scan, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		// Handle action bar item clicks here. The action bar will
		// automatically handle clicks on the Home/Up button, so long
		// as you specify a parent activity in AndroidManifest.xml.
		int id = item.getItemId();
		if (id == R.id.action_settings) {
			return true;
		}
		return super.onOptionsItemSelected(item);
	}

	@Override
	public void didCancel() {
		mBarcodePicker.stopScanning();
        finish();
	}

	@Override
	public void didManualSearch(String entry) {
		Toast.makeText(this, "User entered: " + entry, Toast.LENGTH_LONG).show();
		
	}

	@Override
	public void didScanBarcode(String barcode, String symbology) {
		// Remove non-relevant characters that might be displayed as rectangles
        // on some devices. Be aware that you normally do not need to do this.
        // Only special GS1 code formats contain such characters.
        String cleanedBarcode = "";
        for (int i = 0 ; i < barcode.length(); i++) {
            if (barcode.charAt(i) > 30) {
                cleanedBarcode += barcode.charAt(i);
            }
        }
        
        Toast.makeText(this, symbology + ": " + cleanedBarcode, Toast.LENGTH_LONG).show();
		finish();
	}
	
	@Override
	protected void onPause() {
		// When the activity is in the background immediately stop the 
        // scanning to save resources and free the camera.
        mBarcodePicker.stopScanning();
		super.onPause();
	}
	
	@Override
	protected void onResume() {
		// Once the activity is in the foreground again, restart scanning.
        mBarcodePicker.startScanning();
		super.onResume();
	}
	
	@Override
	public void onBackPressed() {
		mBarcodePicker.stopScanning();
        finish();
		super.onBackPressed();
	}
	
	/**
     * Initializes and starts the bar code scanning.
     */
    public void initializeAndStartBarcodeScanning() {
        // Switch to full screen.
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, 
                             WindowManager.LayoutParams.FLAG_FULLSCREEN);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        
        // We instantiate the automatically adjusting barcode picker that will
        // choose the correct picker to instantiate. Be aware that this picker
        // should only be instantiated if the picker is shown full screen as the
        // legacy picker will rotate the orientation and not properly work in
        // non-fullscreen.
        ScanditSDKAutoAdjustingBarcodePicker picker = new ScanditSDKAutoAdjustingBarcodePicker(
                    this, sScanditSdkAppKey, ScanditSDKAutoAdjustingBarcodePicker.CAMERA_FACING_BACK);
        
        // Add both views to activity, with the scan GUI on top.
        setContentView(picker);
        mBarcodePicker = picker;
        
        // Register listener, in order to be notified about relevant events 
        // (e.g. a successfully scanned bar code).
        mBarcodePicker.getOverlayView().addListener(this);
        
        // Show a search bar in the scan user interface.
        mBarcodePicker.getOverlayView().showSearchBar(true);
    }
	
}
