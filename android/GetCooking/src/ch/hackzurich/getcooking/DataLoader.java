package ch.hackzurich.getcooking;

import java.io.IOException;

import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpParams;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import android.os.AsyncTask;

public class DataLoader {

	public DataLoader() {
	}

	public void getShoppingList(ShoppingListLoaderListener listener) {
		new DownloadShoppingList(listener).execute("http://hackzurich.me/shopping_list");
	}
	public interface ShoppingListLoaderListener {
		public void onShoppingListAvailable(ObjectItem[] objectItemData);
	}

	private class DownloadShoppingList extends AsyncTask<String, Void, JSONObject> {

		private ShoppingListLoaderListener listener;

		public DownloadShoppingList(ShoppingListLoaderListener listener) {
			this.listener = listener;
		}

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
			super.onPostExecute(result);

			ObjectItem[] objectItemData = null;

			try {
				JSONArray items;
				items = result.getJSONArray("ingredients");
				objectItemData = new ObjectItem[items.length()];
				for (int i = 0; i < items.length(); i++) {
					JSONObject obj = items.getJSONObject(i);
					objectItemData[i] = new ObjectItem(obj.getString("title"), obj.getString("ean"));
				}
			} catch (JSONException e) {
				objectItemData = null;
				e.printStackTrace();
			} catch (Exception e) {
				objectItemData = null;
			}

			listener.onShoppingListAvailable(objectItemData);

		}

	}













	public void getIngredientName(IngredientNameListener listener, String barCode) {
		new DownloadIngredientName(listener).execute("http://hackzurich.me/ingredient/" + barCode);
	}
	public interface IngredientNameListener {
		public void onIngredientNameAvailable(String name, String ean);
	}
	private class DownloadIngredientName extends AsyncTask<String, Void, JSONObject> {

		private IngredientNameListener listener;

		public DownloadIngredientName(IngredientNameListener listener) {
			this.listener = listener;
		}

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
			super.onPostExecute(result);

			try {
				JSONObject obj = result.getJSONObject("ingredient");
				String name = obj.getString("title");
				String ean = obj.getString("ean");
				listener.onIngredientNameAvailable(name, ean);
			} catch (JSONException e) {
				e.printStackTrace();
				listener.onIngredientNameAvailable(null, null);
			} catch (Exception e) {
				e.printStackTrace();
				listener.onIngredientNameAvailable(null, null);
			}
			

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
