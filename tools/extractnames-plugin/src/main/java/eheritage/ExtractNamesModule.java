package eheritage;

import org.elasticsearch.common.inject.AbstractModule;

public class ExtractNamesModule extends AbstractModule {

  @Override
  protected void configure() {
    bind(ExtractNamesHandler.class).asEagerSingleton();
  }

}
