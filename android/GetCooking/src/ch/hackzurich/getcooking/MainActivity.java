package ch.hackzurich.getcooking;

import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;

import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.content.Intent;
import android.graphics.Color;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v4.widget.SwipeRefreshLayout.OnRefreshListener;
import android.support.v7.app.ActionBarActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ListView;

public class MainActivity extends ActionBarActivity implements OnRefreshListener {


	private SwipeRefreshLayout mSwipeLayout;
	private ListView mListViewItems;
	private ArrayAdapterItem mAdapter;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		/*Intent intent = new Intent(this, LoginActivity.class);
		startActivity(intent);*/


		setContentView(R.layout.activity_main);
		/*if (savedInstanceState == null) {
			getSupportFragmentManager().beginTransaction()
					.add(R.id.container, new MainFragment()).commit();
		}*/


		mSwipeLayout = (SwipeRefreshLayout) findViewById(R.id.swipe_container);
		mSwipeLayout.setOnRefreshListener(this);
		mSwipeLayout.setColorSchemeColors(Color.RED, Color.GREEN, Color.BLUE, Color.CYAN);


		// add your items, this can be done programatically
		// your items can be from a database
		ObjectItem[] ObjectItemData = new ObjectItem[0];

		// our adapter instance
		mAdapter = new ArrayAdapterItem(this, R.layout.list_view_row_item, ObjectItemData);

		// create a new ListView, set the adapter and item click listener
		mListViewItems = (ListView) findViewById(R.id.listView1);
		mListViewItems.setAdapter(mAdapter);
		//listViewItems.setOnItemClickListener(new OnItemClickListenerListViewItem());

		Button btnScan = (Button) findViewById(R.id.buttonScan);
		btnScan.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) {
				Intent intent = new Intent(MainActivity.this, ScanActivity.class);
				MainActivity.this.startActivity(intent);
			}
		});
		doRefresh();
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
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
	public void onRefresh() {
		doRefresh();
	}

	private void doRefresh() {
		mSwipeLayout.setRefreshing(true);
		new DownloadShoppingList().execute("http://hackzurich.me/shopping_list");

	}


	private class DownloadShoppingList extends AsyncTask<String, Void, JSONObject> {

		@Override
		protected JSONObject doInBackground(String... params) {
			String content = getContent(params[0]);
			if(content == null)
				return null;
			try {
				JSONObject reader = new JSONObject(content);
				return reader;
			} catch (JSONException e) {
				e.printStackTrace();
				return null;
			}
			
		}

		@Override
		protected void onPostExecute(JSONObject result) {
			
			ObjectItem[] objectItemData = null;
			
			try {
				JSONArray items; items = result.getJSONArray("items");
				objectItemData = new ObjectItem[items.length()];
				for (int i = 0; i < items.length(); i++) {
					JSONObject obj = items.getJSONObject(i);
					objectItemData[i] = new ObjectItem(i, obj.getString("name"));
				}
			} catch (JSONException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			mAdapter.data = objectItemData;
			mSwipeLayout.setRefreshing(false);
			mAdapter.notifyDataSetChanged();
			
			super.onPostExecute(result);
		}

	}







	private String getContent(String url) {
		HttpResponse response = null;
		HttpGet httpGet = null;
		HttpClient mHttpClient = null;
		String s = null;

		try {
			if(mHttpClient == null) {
				HttpParams httpParams = new BasicHttpParams();
				//HttpConnectionParams.setConnectionTimeout(httpParams, mTimoutInSeconds * 1000);
				//HttpConnectionParams.setSoTimeout(httpParams, mTimoutInSeconds * 1000);
				mHttpClient = new DefaultHttpClient(httpParams);
			}
			httpGet = new HttpGet(url);

			response = mHttpClient.execute(httpGet);
			if (response != null && response.getStatusLine().getStatusCode() == HttpStatus.SC_OK) {
				s = EntityUtils.toString(response.getEntity(), "UTF-8");
			} else {
				s = null;
			}

		} catch (IOException e) {
			e.printStackTrace();
			s = null;
		} 

		return s;
	}

}
